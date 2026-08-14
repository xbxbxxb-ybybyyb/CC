# coding: utf-8
# Author：fengchi863
# Date ：2020/5/7 17:17

'''
使用深度网络以后，acc可以达到0.92-0.93
'''

import keras
import pandas as pd, numpy as np
from keras.layers.core import Dense, Activation
from keras.utils import plot_model
from keras.models import Model
from keras.layers import Flatten, Input, Reshape, Conv2D
from keras.layers.pooling import MaxPooling2D
from keras.datasets import mnist

num_classes = 10
batch_size = 128
epochs = 12

img_rows, img_cols = 28, 28

path='mnist.npz'
with np.load(path) as f:
    x_train, y_train = f['x_train'], f['y_train']
    x_test, y_test = f['x_test'], f['y_test']

y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

input_shape = (28,28)
inputs = Input(input_shape)
x = Reshape(input_shape + (1, ), input_shape=input_shape)(inputs)
conv1 = Conv2D(14, kernel_size=4, activation='relu')(x) # 一般卷积核为奇数边长，这里设置的偶数
pool1 = MaxPooling2D(pool_size=(2,2))(conv1)
conv2 = Conv2D(7, kernel_size=4, activation='relu')(pool1)
pool2 = MaxPooling2D(pool_size=(2,2))(conv2)
flatten = Flatten()(pool2)
output = Dense(10, activation='sigmoid')(flatten)
model = Model(inputs=inputs, outputs=output)
print(model.summary())

# plot_model(model, to_file='conv_nerual_network.png') # need pydot package

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
