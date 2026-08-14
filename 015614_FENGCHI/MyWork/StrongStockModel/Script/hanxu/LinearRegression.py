from keras.optimizers import adam, sgd, Nadam, RMSprop, Adagrad, Adamax
from keras.models import Sequential, load_model
from keras.callbacks import ReduceLROnPlateau
from keras.layers import Dense


class LinearRegression(object):

    address = '/data/user/015836/HFmodel/linear_5min_180f/'

    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=10, min_lr=0.001)
    model = Sequential()
    model.add(Dense(1, activation='linear', input_shape=(180,)))
    model.compile(optimizer=Adamax(lr=0.1), loss='mean_squared_error', metrics=[])

    def train(self, X, y):

        self.model.fit(x=X, y=y, epochs=1000, batch_size=2 ** 15, callbacks=self.reduce_lr, verbose=2)

    def predict(self, X, y):

        return self.model.predict(X).flatten()

    def save(self, file):

        self.model.save(self.address + '/conf/%s.h5' % file)

    def load(self, file):

        self.model = load_model(self.address + '/conf/%s.h5' % file)