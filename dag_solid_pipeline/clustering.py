import io

import requests

import pandas as pd
import pylab as plt
from dagster import (InputDefinition, Int, OutputDefinition, String, pipeline,
                     repository, solid)
from sklearn.cluster import KMeans
from utils.dagster_types import PandasDataFrame


# @solid(required_resource_keys={"warehouse"})
@solid(
    input_defs=[InputDefinition(name="url", dagster_type=String)],
    output_defs=[OutputDefinition(PandasDataFrame)],
)
def read_iris_csv(context, url):
    s = requests.get(url).text
    df = pd.read_csv(io.StringIO(s))
    # context.resources.warehouse.update_records(df)
    return df


@solid(
    config_schema={"clusters": Int, "mapper": dict},
    input_defs=[InputDefinition(name="df", dagster_type=PandasDataFrame)],
    output_defs=[OutputDefinition(PandasDataFrame)],
)
def run_kmean(context, df):
    X = df.iloc[:, 0:3].values
    clusters = context.solid_config["clusters"]
    context.log.info(f"Running k means on {clusters}")
    kmeans = KMeans(n_clusters=clusters).fit(X)
    c = kmeans.predict(X)
    mapper = context.solid_config["mapper"]
    df["Predicted"] = pd.Series([mapper[str(i)] for i in c])
    return df


@solid(config_schema={"mapper": dict})
def plot_clusters(context, df):
    color_mapper = context.solid_config["mapper"]
    plt.figure(figsize=(12, 5))
    plt.subplot(121)
    plt.scatter(df["PetalLength"], df["PetalWidth"], c=df["Name"].map(color_mapper))
    plt.title("Original classes")
    plt.subplot(122)
    plt.scatter(
        df["PetalLength"], df["PetalWidth"], c=df["Predicted"].map(color_mapper)
    )
    plt.title("Predicted classes")
    plt.tight_layout()
    plt.show()


@pipeline
def serial_pipeline():
    model_df = run_kmean(read_iris_csv())
    plot_clusters(model_df)


@repository
def clustering_repository():
    return [serial_pipeline]
