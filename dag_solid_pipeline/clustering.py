import io

import requests

import numpy as np
import pandas as pd
import pylab as plt
from dagster import (Array, InputDefinition, Int, OutputDefinition, String,
                     pipeline, repository, solid)
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
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
    input_defs=[InputDefinition(name="df", dagster_type=PandasDataFrame)],
    # output_defs=[OutputDefinition(Array)],
)
def transform_to_array(context, df):
    return df.iloc[:, 0:3].values


@solid(
    config_schema={"clusters": Int, "mapper": dict},
    # input_defs=[InputDefinition(name="X", dagster_type=Array)],
)
def run_kmean(context, X):

    clusters = context.solid_config["clusters"]
    context.log.info(f"Running k means with {clusters} clusters")
    model = KMeans(n_clusters=clusters, random_state=42).fit(X)
    return model


@solid
def add_predictions(context, model, X):
    c = model.predict(X)
    mapper = context.solid_config["mapper"]
    return pd.Series([mapper[str(i)] for i in c])


@solid(config_schema={"mapper": dict})
def plot_clusters(context, df, preds):
    color_mapper = context.solid_config["mapper"]
    plt.figure(figsize=(12, 5))
    plt.subplot(121)
    plt.scatter(df["PetalLength"], df["PetalWidth"], c=df["Name"].map(color_mapper))
    plt.title("Original classes")
    plt.subplot(122)
    plt.scatter(df["PetalLength"], df["PetalWidth"], c=preds.map(color_mapper))
    plt.title("Predicted classes")
    plt.tight_layout()
    plt.show()


@pipeline
def serial_pipeline():
    df = read_iris_csv()
    model = run_kmean(transform_to_array(df))
    preds = add_predictions(model, transform_to_array(df))
    plot_clusters(df, preds)


@repository
def clustering_repository():
    return [serial_pipeline]
