
from LimitUpPredStrategy.model.ModelBase.ModelBaseReg import ModelBaseReg
from keras.models import Sequential
from keras.layers import Dense,Dropout,Activation
from keras.optimizers import Adam
import pandas as pd

class DNNModelReg(ModelBaseReg):
    def __init__(self, start_date=20140101, end_date=20191231, stock_pool_address=None):
        super().__init__(start_date, end_date, stock_pool_address)

    def train_model(self, X_train, y_train, params):
        adam = Adam(lr=0.0001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=5e-04)
        n = len(y_train)
        x_train = X_train[:int(n*0.9)]
        y1 = y_train[:int(n*0.9)]
        x_test = X_train[int(n * 0.9):]
        y2 = y_train[int(n * 0.9):]
        model = Sequential()
        model.add(Dense(16, input_shape=(X_train.shape[1],)))
        model.add(Activation('relu'))
        model.add(Dense(32))
        model.add(Activation('relu'))
        model.add(Dense(64))
        model.add(Activation('relu'))
        model.add(Dense(32))
        model.add(Activation('relu'))
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer=adam)
        model.fit(x_train, y1,epochs=20,batch_size=64,validation_data=(x_test, y2), verbose=2, shuffle=False,)
        return model

    def predict(self, model, X_test, true_pct=0.5):
        predict = model.predict(X_test)
        predict = pd.DataFrame(predict.reshape(-1, 1), index=X_test.index)
        return predict
