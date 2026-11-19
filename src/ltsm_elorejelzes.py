from tensorflow import keras

modell = keras.Sequential([
    keras.Input(shape=(5, 1)),  # 5 év, évenként 1 hőmérséklet
    keras.layers.LSTM(4),
    keras.layers.Dense(1),      # A következő év becsült átlaga
])

modell.compile(optimizer="adam", loss="mse")
