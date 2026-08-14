# @Time : 2021/8/3 10:53
# @Author : Zhichen Lu
# @File : ParamSeeking.py


import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
from keras.callbacks import *
from keras.layers import Dropout, Dense,BatchNormalization
import keras.backend as K
from keras.optimizers import SGD
from keras.models import Sequential
from StrongStockModel.model.ModelBase.ModelNewLoading import ModelNewLoading
import os,time,gc,datetime
from StrongStockModel.conf.path_config import root_path
from tqdm import tqdm
from dataApi.tradeDate import get_date_range,get_pre_trade_date
from xquant.compute.aimr import AIMR
from keras.losses import mse

# y_true_ = train_label[:10000].values
# y_pred_ = model.predict(train_features[:10000].values)
def K_corr(y_true_, y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return K.mean((y_true - K.mean(y_true,axis=0))*(y_pred-K.mean(y_pred,axis=0)),axis=0)/( K.std(y_true,axis=0) * K.std(y_pred,axis=0))


def K_inter_corr(y_pred_):
    y_pred = K.cast(y_pred_,dtype='float32')
    normlize_y = (y_pred - K.mean(y_pred,axis=0))/K.std(y_pred,axis=0)
    ones = (normlize_y+100)/(normlize_y+100)
    corr = K.dot(K.transpose(normlize_y),normlize_y)/K.sum(ones,axis=0)
    return K.mean(corr*corr)


def myloss(y_true_, y_pred_):

    corr = K_corr(y_true_, y_pred_)
    inter_corr = K_inter_corr(y_pred_)
    mean_corr = K.mean(corr*corr)

    # std_corr = K.std(corr)
    return 1+0.3*inter_corr - mean_corr
    # y_true, y_pred = K.cast(y_true_,dtype='float32'),K.cast(y_pred_,dtype='float32')
    # return mean_squared_error(y_pred,y_true) + 2*K_corr(y_true_,y_pred_)

best_param_clf_nn = {
    'activation': 'relu',
    'hidden_layer_sizes': (200,100),
    'learning_rate': 'adaptive',
    'learning_rate_init': 0.1,
    'momentum': 0.5, 'solver': 'sgd',
    'nb_epoch': 200,
    'batch_size': 2 ** 15
}


def NN(input_dim, params):
    hidden_layer_sizes = params['hidden_layer_sizes']
    model = Sequential()
    model.add(Dense(hidden_layer_sizes[0], input_dim=input_dim, activation=params['activation']))
    model.add(Dropout(0.4))
    model.add(BatchNormalization(momentum=0.8))
    for dim in hidden_layer_sizes[1:-1]:
        model.add(Dropout(0.3))
        model.add(Dense(dim, activation=params['activation']))
        model.add(BatchNormalization(momentum=0.5))
    model.add(Dropout(0.3))
    model.add(Dense(hidden_layer_sizes[-1], activation=params['activation']))
    model.add(BatchNormalization(momentum=0.5))
    optimizer = SGD(lr=params['learning_rate_init'], momentum=params['momentum'])
    # self.compile_model(model, optimizer, [])
    model.compile(loss=myloss, optimizer=optimizer, metrics=[])
    # print(model.summary())
    return model

model_conf_path = f'{root_path}TempData/model_conf/'
log_path = f'{root_path}TempData/log/'

if not os.path.exists(model_conf_path):
    os.makedirs(model_conf_path)
if not os.path.exists(log_path):
    os.makedirs(log_path)

params = best_param_clf_nn.copy()

idx = 3
X_train,y_train = pd.read_pickle(f'{root_path}TempData/TrainSetForNNexTractorOpt.pkl')


model = NN(input_dim=X_train.shape[1], params=params)
early_stopping = EarlyStopping(monitor='val_loss', patience=15)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                              patience=5, min_lr=0.001)
train_log = CSVLogger(log_path + '%d.csv' % idx)
callbacks_list = [early_stopping, reduce_lr, train_log]

model.fit(X_train.values, y_train.values, epochs=params['nb_epoch'], \
          batch_size=params['batch_size'], verbose=1, \
          shuffle=True, callbacks=callbacks_list, validation_split=0.1)
model.save_weights(model_conf_path + '%d.h5' % idx)
model.load_weights(model_conf_path + '%d.h5' % idx)
X_test,y_test = pd.read_pickle(f'{root_path}TempData/TestSetForNNexTractorOpt.pkl')
train_log = pd.read_csv(log_path + '%d.csv' % idx)
# a = pd.Series({each:y_test.corrwith(X_test[each]) for each in X_test.columns})
# a.apply(lambda x : x['actual_label'])
Feature_test = model.predict(X_test.values)

Feature_test = pd.DataFrame(Feature_test)
Feature_test.index = y_test.index
Feature_test['label'] = y_test
corr = Feature_test.corr()
corr_label = corr['label'].drop('label')
corr_label.mean()