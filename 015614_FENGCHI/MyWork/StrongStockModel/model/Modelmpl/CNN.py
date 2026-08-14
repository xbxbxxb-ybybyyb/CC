# coding: utf-8
# Author：fengchi863
# Date ：2020/8/10 16:58

import pandas as pd
from keras.callbacks import *
from keras.layers import Conv1D, Dropout, Flatten, Dense, BatchNormalization, Activation
from keras.layers.pooling import AveragePooling1D
from keras.models import Sequential
from sklearn import metrics

from StrongStockModel.conf.path_config import cnn_model_path
from StrongStockModel.model.ModelBase.ModelBase import ModelBase


class CNN(ModelBase):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None):
        super().__init__(start, end, stock_pool, feature_address)

    def CNN(self, input_dim, output_dim, params):
        model = Sequential()
        model.add(Conv1D(filters=params["input_filter"],
                         kernel_size=params["input_kernel_size"],
                         strides=params["input_strides"],
                         input_shape=(input_dim, 1)))
        if params['batch_norm'] is True:
            model.add(BatchNormalization())
        model.add(Activation(params['input_activation']))
        model.add(Dropout(params['input_dropout']))
        ## conv layer
        conv_layers = params['conv_layers']
        while conv_layers > 0:
            model.add(Conv1D(filters=params['hidden_filter'],
                             kernel_size=params['hidden_kernel_size'],
                             strides=params['hidden_strides']))
            if params['batch_norm'] is True:
                model.add(BatchNormalization())
            model.add(Activation(params['conv_activation']))
            model.add(Dropout(params['conv_dropout']))
            conv_layers -= 1
        if params['pooling'] is True:
            model.add(AveragePooling1D(pool_size=2, strides=2))
        # dense layer
        model.add(Flatten())
        hidden_layers = params['hidden_layers']
        while hidden_layers > 0:
            dim = params['hidden_units']
            model.add(Dense(dim, activation=params["hidden_activation"]))
            model.add(Dropout(params["hidden_dropout"]))
            hidden_layers -= 1
        # code layer
        model.add(Dense(output_dim, activation='sigmoid'))
        self.compile_model(model, params["opt_optimizer"])
        print(model.summary())
        return model

    def compile_model(self, model4compile, opt_er, metrics_eval=['accuracy']):
        model4compile.compile(loss='binary_crossentropy', \
                              optimizer=opt_er, metrics=metrics_eval)
        return model4compile

    def train_model(self, X_train, y_train, params):
        X_train = np.expand_dims(X_train.values, 2)
        y_train = y_train.values
        model = self.CNN(input_dim=X_train.shape[1], output_dim=1, params=params)
        early_stopping = EarlyStopping(monitor='acc', patience=10)
        checkpoint = ModelCheckpoint(cnn_model_path + 'cnn_0811.h5', monitor='acc', \
                                     verbose=1, save_best_only=True, \
                                     mode='max')
        callbacks_list = [checkpoint, early_stopping]
        model.fit(X_train, y_train, epochs=params['nb_epoch'], \
                  batch_size=params['batch_size'], verbose=0, \
                  shuffle=False, callbacks=callbacks_list)
        model.load_weights(cnn_model_path + 'cnn_0811.h5')
        model = self.compile_model(model, params['opt_optimizer'])
        return model

    def predict(self, model, X_test):
        X_test = np.array(X_test)
        X_test = np.expand_dims(X_test, 2)
        pre_label = model.predict(X_test)
        return pre_label

    def training_methodology(self, params, period=10, predict_period=10):
        compare = self.rolling_train_and_predict(params=params, period=period, predict_period=predict_period)
        if len(compare) == 0:
            return pd.DataFrame(), {'acc': np.nan, 'precision': np.nan, 'recall': np.nan, 'f1': np.nan}
        acc = metrics.accuracy_score(y_true=compare['actual_label'], y_pred=compare['prediction'])
        precision = metrics.precision_score(y_true=compare['actual_label'], y_pred=compare['prediction'],
                                            average='micro')
        recall = metrics.recall_score(y_true=compare['actual_label'], y_pred=compare['prediction'], average='micro')
        f1 = metrics.f1_score(y_true=compare['actual_label'], y_pred=compare['prediction'], average='micro')
        print({'acc': acc, 'precision': precision, 'recall': recall, 'f1': f1})
        return compare, {'acc': acc, 'precision': precision, 'recall': recall, 'f1': f1}
