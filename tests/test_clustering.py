from dag_solid_pipeline.clustering import serial_pipeline
from dagster import execute_pipeline, execute_solid


def test_clustering_pipeline():
    res = execute_pipeline(
        serial_pipeline,
        run_config={
            "solids": {
                "read_iris_csv": {
                    "inputs": {
                        "url": "https://raw.githubusercontent.com/pandas-dev/pandas/master/pandas/tests/io/data/csv/iris.csv"
                    }
                },
                "run_kmean": {"config": {"clusters": 3}},
                "add_predictions": {
                    "config": {
                        "mapper": {
                            "0": "Iris-versicolor",
                            "1": "Iris-setosa",
                            "2": "Iris-virginica",
                        }
                    }
                },
                "plot_clusters": {
                    "config": {
                        "mapper": {
                            "Iris-versicolor": "red",
                            "Iris-setosa": "green",
                            "Iris-virginica": "blue",
                        }
                    }
                },
            }
        },
    )
    assert res.success
