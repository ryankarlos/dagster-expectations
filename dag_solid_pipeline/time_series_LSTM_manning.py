import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from io_utils.load_data import get_data_dir_path, read_csv_from_gh

URL = "https://github.com/facebook/prophet/blob/master/examples/example_wp_log_peyton_manning.csv"
FILENAME = "manning.csv"
FILEPATH = os.path.join(get_data_dir_path(), FILENAME)
WINDOW_SIZE = 70
BATCH_SIZE = 64
SHUFFLE_BUFFER_SIZE = 1000
SPLIT_TIME = 2920
EPOCHS = 20


def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[1:]))
    return ds.batch(batch_size).prefetch(1)


def train_test_split_series_time(series, time, split_time):
    time_train = time[:split_time]
    x_train = series[:split_time]
    time_valid = time[split_time:]
    x_valid = series[split_time:]
    return time_train, x_train, time_valid, x_valid


def build_rnn_timeseries_model():
    return tf.keras.models.Sequential(
        [
            tf.keras.layers.Conv1D(
                filters=60,
                kernel_size=5,
                strides=1,
                padding="causal",
                activation="relu",
                input_shape=[None, 1],
            ),
            tf.keras.layers.LSTM(60, return_sequences=True),
            tf.keras.layers.LSTM(60, return_sequences=True),
            tf.keras.layers.Dense(30, activation="relu"),
            tf.keras.layers.Dense(10, activation="relu"),
            tf.keras.layers.Dense(1),
            tf.keras.layers.Lambda(lambda x: x * 400),
        ]
    )


def compile_model(model):
    optimizer = tf.keras.optimizers.SGD(lr=1e-5, momentum=0.9)
    model.compile(loss=tf.keras.losses.Huber(), optimizer=optimizer, metrics=["mae"])


def model_forecast(model, series, window_size):
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size))
    ds = ds.batch(32).prefetch(1)
    forecast = model.predict(ds)
    return forecast


def plot_series(time, series, format="-", start=0, end=None):
    plt.plot(time[start:end], series[start:end], format)
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.grid(True)
    plt.show()


def compute_loss(history):
    """
    Computes training and val loss and accuracy
    """
    loss = history.history["loss"]
    mae = history.history["mae"]

    return mae, loss


def plot_acc_loss(history):
    """
    Plots the chart for accuracy and loss on both training and validation
    """

    mae, loss = compute_loss(history)
    epochs = range(len(mae))
    plt.figure()
    plt.title("Training and validation loss")
    plt.plot(epochs, mae, "r", label="mae")
    plt.plot(epochs, loss, "b", label="Training Loss")
    plt.legend()

    return plt


if __name__ == "__main__":
    if not os.path.exists("data/manning.csv"):
        read_csv_from_gh(URL, FILEPATH, overwrite=True)
    df = pd.read_csv("data/manning.csv")
    time = df["ds"]
    series = df["y"]
    time_train, x_train, time_valid, x_valid = train_test_split_series_time(
        series, time, SPLIT_TIME
    )

    train_set = windowed_dataset(
        x_train,
        window_size=WINDOW_SIZE,
        batch_size=BATCH_SIZE,
        shuffle_buffer=SHUFFLE_BUFFER_SIZE,
    )

    model = build_rnn_timeseries_model()
    compile_model(model)
    history = model.fit(train_set, epochs=EPOCHS)
    plt = plot_acc_loss(history)
    plt.show()
    # rnn_forecast = model_forecast(model, series[..., np.newaxis], window_size)
    # rnn_forecast = rnn_forecast[split_time - window_size : -1, -1, 0]
    # mae = tf.keras.metrics.mean_absolute_error(x_valid, rnn_forecast).numpy()
    # print(f"Mean Absolute Error: {mae}")
