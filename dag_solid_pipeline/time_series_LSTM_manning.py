import pandas as pd
import tensorflow as tf
from io_utils.load_data import read_csv_from_gh

window_size = 60
batch_size = 100
shuffle_buffer_size = 1000
split_time = 2500
epochs = 50


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


if __name__ == "__main__":
    df = pd.read_csv('data/manning.csv')
    time = df['ds']
    series = df['y']
    time_train, x_train, time_valid, x_valid = train_test_split_series_time(
        series, time, split_time
    )

    train_set = windowed_dataset(
        x_train,
        window_size=window_size,
        batch_size=batch_size,
        shuffle_buffer=shuffle_buffer_size,
    )

    model = build_rnn_timeseries_model()
    compile_model(model)
    history = model.fit(train_set, epochs=epochs)
    rnn_forecast = model_forecast(model, series[..., np.newaxis], window_size)
    rnn_forecast = rnn_forecast[split_time - window_size: -1, -1, 0]
    mae = tf.keras.metrics.mean_absolute_error(x_valid, rnn_forecast).numpy()
    print(f"Mean Absolute Error: {mae}")