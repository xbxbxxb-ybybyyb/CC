# coding: utf-8
# Author：fengchi863
# Date ：2020/5/6 14:01

import keras
import pandas as pd, numpy as np
from keras.layers.core import Dense, Activation
from keras.utils import plot_model
from keras.models import Sequential
from keras.layers import Flatten
from keras.datasets import mnist

num_classes = 10
batch_size = 128
epochs = 12

img_rows, img_cols = 28, 28

path='mnist.npz'
f = np.load(path)
x_train, y_train = f['x_train'], f['y_train']
x_test, y_test = f['x_test'], f['y_test']
f.close()

y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

# notes: 有时候层数多也不好，比如我注释掉的这一层，加上以后acc反而变成0.85，不加是0.89
model = Sequential([
    Flatten(input_shape=(28,28)),
    Dense(32, input_dim=784),
    Activation("sigmoid"),
    # Dense(16),
    # Activation("sigmoid"),
    Dense(10),
    Activation("softmax"),
])

print(model.summary)

opt = keras.optimizers.rmsprop(lr=0.0001, decay=1e-6)

model.compile(loss='categorical_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

model.fit(x_train, y_train,
          batch_size=batch_size,
          epochs=epochs,
          validation_data=(x_test, y_test),
          shuffle=True)

print('finished fitting!')

scores = model.evaluate(x_test, y_test, verbose=False)
print('Test loss:', scores[0])
print('Test accuracy:', scores[1])