import numpy as np
import pandas as pd
from sklearn import metrics
from keras.optimizers import adam, sgd, Nadam, RMSprop, Adagrad, Adamax
from keras.models import Sequential, load_model
from keras.callbacks import ReduceLROnPlateau
from keras.layers import Dense
import os
from StrongStockModel.model.ModelBase.ModelBase import ModelBase
from StrongStockModel.conf.path_config import fix_factor_true_send_ic_sort_path
import datetime, time, gc
from tqdm import tqdm

class LinearRegression(ModelBase):

    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None):
        super().__init__(start, end, stock_pool, feature_address)

    def train_model(self, X_train, y_train, params, end_date=None):

        date_list = sorted(list(set(X_train.index.get_level_values(0))))
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9]]
        train_end = date_list[-1]
        date_list = sorted(list(set(date_list) - set(val_date)))
        train_features, train_label = X_train.loc[date_list].values, y_train.loc[date_list]

        reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=10, min_lr=0.001)

        activation = 'linear' if 'activation' not in params else params['activation']
        optimizer = 'adam' if 'optimizer' not in params else params['optimizer']
        loss = 'mean_squared_error' if 'loss' not in params else params['loss']
        metrics = [] if 'metrics' not in params else params['metrics']
        epochs = 50 if 'epochs' not in params else params['epochs']
        callbacks = [reduce_lr] if 'callbacks' not in params else params['callbacks']
        verbose = 0 if 'verbose' not in params else params['verbose']

        batch_size = 2 ** 20 if 'batch_size' not in params else params['batch_size']
        batch_size = max(batch_size, train_features.shape[0] // batch_size)

        if 'load local model' in params and os.path.exists(params['model_conf_path'] + '%d.h5' % train_end):
            model = load_model(params['model_conf_path'] + '%d.h5' % train_end)
            print('load from local', train_end)
            return model

        model = Sequential()
        model.add(Dense(1, activation=activation, input_shape=(train_features.shape[1], )))
        model.compile(optimizer=Adamax(lr=0.1), loss=loss, metrics=metrics)
        model.fit(x=train_features, y=train_label.values, epochs=1000,
                  batch_size=train_features.shape[0], callbacks=callbacks, verbose=verbose)

        model.save(params['model_conf_path'] + '%d.h5' % end_date)
        print(params['model_conf_path'] + '%d.h5' % end_date)

        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            val_features, val_labels = X_train.loc[val_date].values, y_train.loc[val_date]
            val_labels['prediction'] = model.predict(val_features).flatten()
            pd.to_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % end_date)

        if 'train_pred_path' in params:
            if not os.path.exists(params['train_pred_path']):
                os.mkdir(params['train_pred_path'])
            train_label['prediction'] = model.predict(train_features).flatten()
            pd.to_pickle(train_label, params['train_pred_path'] + '%d.pkl' % end_date)

        return model

