import vaex
vaex.multithreading.thread_count_default = 8
import vaex.ml
import numpy as np
import pylab as plt
import csv
import os
from dagster import pipeline, solid
import vaex.ml.cluster


@solid
def load_iris(context):
    df = vaex.ml.datasets.load_iris()
    context.log.info(f"loaded iris dataset into vaex df".format())
    return df

@solid
def run_kmean(_, data):
    features = ['petal_length', 'petal_width', 'sepal_length', 'sepal_width']
    kmeans = vaex.ml.cluster.KMeans(features=features, n_clusters=3, max_iter=100, verbose=True, random_state=42)
    kmeans.fit(data)
    return kmeans.transform(data)

@solid
def map_cluster_id_to_labels(_, data):
    data['predicted_kmean_map'] = data.prediction_kmeans.map(mapper={0: 1, 1: 2, 2: 0})
    return data

@solid
def plot_clusters(_, data):
    fig = plt.figure(figsize=(12, 5))
    plt.subplot(121)
    data.scatter(data.petal_length, data.petal_width, c_expr=data.class_)
    plt.title('Original classes')
    plt.subplot(122)
    data.scatter(data.petal_length, data.petal_width, c_expr=data.predicted_kmean_map)
    plt.title('Predicted classes')
    plt.tight_layout()
    plt.show()

@pipeline
def serial_pipeline():
    model = run_kmean(load_iris())
    remap = map_cluster_id_to_labels(model)
    plot_clusters(remap)
