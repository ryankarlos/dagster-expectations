import io

import requests
import yaml

import pandas as pd
import pylab as plt
from dagster import (
    InputDefinition,
    Int,
    ModeDefinition,
    OutputDefinition,
    String,
    execute_pipeline,
    fs_io_manager,
    pipeline,
    repository,
    solid,
)
from dagster_io.postgres import postgres_warehouse_resource
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from utils.dagster_types import PandasDataFrame


# @solid(required_resource_keys={"warehouse"})
@solid(
    input_defs=[InputDefinition(name="url", dagster_type=String)],
    output_defs=[OutputDefinition(dagster_type=PandasDataFrame)],
    required_resource_keys={"postgres"},
)
def read_iris_csv(context, url):
    s = requests.get(url).text
    df = pd.read_csv(io.StringIO(s))
    if context.mode_def.name == "db":
        context.resources.postgres.handle_data_output(context, df)
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
def add_predictions(context, model, df, X):
    c = model.predict(X)
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


@pipeline(
    mode_defs=[
        ModeDefinition(
            name="file",
            resource_defs={
                "io_manager": fs_io_manager.configured(
                    {"base_dir": "/Users/rk1103/Documents/tmp"}
                ),
                "postgres": postgres_warehouse_resource,
            },
        ),
        ModeDefinition(
            name="db", resource_defs={"postgres": postgres_warehouse_resource}
        ),
    ]
)
def serial_pipeline():
    df = read_iris_csv()
    X = transform_to_array(df)
    model = run_kmean(X)
    df_preds = add_predictions(model, df, X)
    plot_clusters(df_preds)


@repository
def clustering_repository():
    return [serial_pipeline]


if __name__ == "__main__":
    with open("dagster_config/run_config.yaml") as f:
        run_config = yaml.load(f, Loader=yaml.FullLoader)
    execute_pipeline(serial_pipeline, run_config=run_config, mode="db")
