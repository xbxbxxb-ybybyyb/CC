# @Time : 2020/11/4 8:54
# @Author : Zhichen Lu
# @File : RNNBase.py

import pandas as pd
from keras.callbacks import *
from keras.layers import  Dropout,SimpleRNN,Input,Reshape,LSTM
from keras import Model
from keras.losses import mean_squared_error
import keras.backend as K
from keras.optimizers import SGD
from keras.models import Sequential
from sklearn import metrics
import tensorflow as tf
import gc
from keras.applications import resnet50
from StrongStockModel.model.ModelBase.ModelBase import ModelBase
from dataApi.DataPrepare import DataPrepare
from dataApi.tradeDate import get_desample_minute_dict
from tqdm import tqdm
import gc,time,datetime

time_list = get_desample_minute_dict(5)
time_list = list(set([time_list[x] for x in time_list]))
time_list.sort()
param_rnn = {'hidden_dim':(16,1),'input_drop_rate':0.4,'recurrent_dropout':0.4,'full_conn_dropout':0.4,
                 'optimizer':'sgd','learning_rate_init':0.1,'momentum':0.6,'nb_epoch':50,'batch_size':2**10}


"""
def my_loss(y_true_,y_pred_):
    y_pred,y_true = K.cast(y_pred_,'float32'),K.cast(y_true_,'float32')
    return 0.5*(1-K.mean((K.transpose(y_true) - K.mean(y_true,axis=1))*(K.transpose(y_pred) - K.mean(y_pred,axis=1)),axis=0)/(K.std(y_true,axis=1)*K.std(y_pred,axis=1))) + \
           K.std(y_true-y_pred,axis=1)

def K_corr(y_true_,y_pred_):
    y_pred,y_true = K.cast(y_pred_,'float32'),K.cast(y_true_,'float32')
    return 0.5*(1-K.mean((K.transpose(y_true) - K.mean(y_true,axis=1))*(K.transpose(y_pred) - K.mean(y_pred,axis=1)),axis=0)/(1e-4+K.std(y_true,axis=1)*K.std(y_pred,axis=1)))

def K_corr(y_true_,y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return (1-K.mean((y_true-K.mean(y_true))*(y_pred-K.mean(y_pred)))/(K.std(y_true)*K.std(y_pred)))

def ts_std(y_true_,y_pred_):
    y_pred,y_true = K.cast(y_pred_,'float32'),K.cast(y_true_,'float32')
    return K.std(y_true-y_pred,axis=1)
"""


def K_corr(y_true_,y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return (1-K.mean((y_true-K.mean(y_true))*(y_pred-K.mean(y_pred)))/(K.std(y_true)*K.std(y_pred)))


def res_std(y_true_, y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return K.std(y_true - y_pred)


def myloss(y_true_, y_pred_):
    return 0.5 * K_corr(y_true_, y_pred_) + res_std(y_true_, y_pred_)



# def Network(input_shape, param=None):
#     inputs = Input(input_shape, name='daily_factor_sequence')
#     # x = Dropout(param['input_drop_rate'],name='drop_between_input_and_RNN')(inputs)
#     x = LSTM(param['hidden_dim'][0], dropout=param['full_conn_dropout'], recurrent_dropout=param['recurrent_dropout'], return_sequences=True, name='')(inputs)
#     for cell_num in param['hidden_dim'][1:]:
#         x = LSTM(cell_num, dropout=param['full_conn_dropout'], recurrent_dropout=param['recurrent_dropout'], return_sequences=True, name='')(x)
#     x = Reshape((input_shape[0],))(x)
#     model = Model(inputs=inputs, outputs=x)
#     optimizer = SGD(lr=param['learning_rate_init'], momentum=param['momentum'])
#     model.compile(optimizer=optimizer, loss=K_corr, metrics=['mae', 'mse'])
#     return model


def ts_stf_mse(y_true_,y_pred_):
    y_pred,y_true = K.cast(y_pred_,'float32'),K.cast(y_true_,'float32')
    return 0.5*K.std(y_true-y_pred,axis=1)+mean_squared_error(y_true,y_pred)


class RNNBase(ModelBase):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None):
        super().__init__(start, end, stock_pool, feature_address)
        if feature_address is None:
            self.dp = DataPrepare()
        else:
            self.dp = DataPrepare(idx_address=feature_address)

    def predict(self, model, X_test, end_date=None):
        pred_label = model.predict(X_test)
        return pred_label

    def feature_engineering(self, train_feature, train_label, test_feature, test_label,train_index,test_index):
        train_feature_nan_rate = np.sum(np.isnan(train_feature),axis=(1,2))/(train_feature.shape[1]*train_feature.shape[2])
        train_label_nan = np.isnan(train_label).sum(axis=1)
        train_label_ts_std = np.std(train_label,axis=1)

        test_feature_nan_rate = np.sum(np.isnan(test_feature),axis=(1,2))/(test_feature.shape[1]*test_feature.shape[2])
        test_label_nan = np.isnan(test_label).sum(axis=1)

        valid_train = (train_feature_nan_rate<0.2) & (train_label_nan==0) & (train_label_ts_std>1e-4)
        valid_test = (test_feature_nan_rate<0.2) & (test_label_nan==0)
        train_index,test_index = pd.Series(valid_train,index=train_index.index), pd.Series(valid_test,index=test_index.index)
        train_index, test_index = train_index[train_index],test_index[test_index]
        train_feature,test_feature,train_label,test_label = train_feature[valid_train],test_feature[valid_test],train_label[valid_train],test_label[valid_test]
        train_feature[train_feature == np.inf] = 5
        train_feature[train_feature == -np.inf] = -5
        train_feature[np.isnan(train_feature)] = 0

        test_feature[test_feature == np.inf] = 5
        test_feature[test_feature == -np.inf] = -5
        test_feature[np.isnan(test_feature)] = 0

        return train_feature, train_label, test_feature, test_label,train_index,test_index

    def get_dataset(self, train_idx, test_idx, fix_factor_list, interday_factor, label_method, label_param={}, kernel=10):
        gc.collect()
        e = time.time()
        self.dp.set_date_range(train_idx[0], test_idx[1])
        fix_factor = self.dp.load_data(fix_factor_list + ['future'])
        load_time = time.time() - e
        date_stk_list = sorted(list(set([(x[0], x[2]) for x in fix_factor.index])))
        date_stk_list = pd.Series(list(range(len(date_stk_list))),index=pd.MultiIndex.from_tuples(date_stk_list))+1
        bar_list = sorted(list(set([x[1] for x in fix_factor.index])))
        daily_ts_feature = fix_factor.swaplevel(1, 2).sort_index()
        daily_ts_feature = daily_ts_feature.values.reshape((fix_factor.shape[0] // 48, 48, fix_factor.shape[-1]))
        split_point = date_stk_list.loc[:train_idx[-1]].shape[0]
        train_feature,train_label = daily_ts_feature[:split_point,:,:-1],daily_ts_feature[:split_point,:,-1]
        test_feature,test_label = daily_ts_feature[split_point:,:,:-1],daily_ts_feature[split_point:,:,-1]
        load_time = time.time() - e

        print('load %d ' % (load_time))
        e = time.time()
        train_index,test_index = date_stk_list.loc[:train_idx[-1]],date_stk_list.loc[test_idx[0]:]
        train_feature, train_label, test_feature, test_label,train_index,test_index = \
            self.feature_engineering(train_feature, train_label, test_feature, test_label,train_index,test_index)
        gc.collect()
        return train_feature, train_label, test_feature, test_label,train_index,test_index, time.time() - e

    def get_fix_factor_evaluation(self, num):
        res = pd.read_excel('/data/group/800319/junkData/StrongStock/external_data/5min样本内.xlsx', index_col=0).sort_index()
        # factor_list = res.loc[1000:2201].sort_values('ic_all_t',ascending=False).index.tolist()[:200]+\
        #                 res.loc[8000:8072].index.tolist()+\
        #                 res.loc[9500:].index.tolist()
        factor_list = res.sort_values('ic_all_t', ascending=False).index.tolist()[:num]
        factor_list = [str(x).zfill(4) for x in factor_list]
        print('JT Factor!')
        return factor_list

    def Network(self,input_shape,param=None):

        inputs = Input(input_shape,name='daily_factor_sequence')
        # x = Dropout(param['input_drop_rate'],name='drop_between_input_and_RNN')(inputs)
        x = SimpleRNN(param['hidden_dim'][0], dropout=param['full_conn_dropout'], recurrent_dropout=param['recurrent_dropout'], return_sequences=True, name='')(inputs)
        for cell_num in param['hidden_dim'][1:]:
            x = SimpleRNN(cell_num, dropout=param['full_conn_dropout'], recurrent_dropout=param['recurrent_dropout'], return_sequences=True,name='')(x)
        x = Reshape((input_shape[0],))(x)
        model = Model(inputs=inputs,outputs=x)
        optimizer = SGD(lr=param['learning_rate_init'], momentum=param['momentum'])
        model.compile(optimizer=optimizer,loss=myloss,metrics=['mae','mse'])
        print('my_loss')
        return model

    def train_model(self, X, y_train, params, end_date=None):
        if not os.path.exists(params['train_log_path']):
            os.mkdir(params['train_log_path'])
        if not os.path.exists(params['model_conf_path']):
            os.mkdir(params['model_conf_path'])
        X_train,train_index = X
        date_list = sorted(list(set([x[0] for x in train_index.index])))
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9]]
        date_list = list(set(date_list) - set(val_date))
        train_id, val_id = pd.Series(False,index = train_index.index),pd.Series(False,index = train_index.index)
        train_id.loc[date_list] = True
        val_id.loc[val_date] = True
        train_features, train_label = X_train[train_id.values], y_train[train_id.values]

        model = self.Network(input_shape=X_train.shape[1:], param=params)
        # model = Network(input_shape=X_train.shape[1:], param=params)
        early_stopping = EarlyStopping(monitor='val_loss', patience=7)
        reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.6,
                                      patience=3, min_lr=0.000001)
        train_log = CSVLogger(params['train_log_path'] + '%d.csv' % val_date[0])
        callbacks_list = [early_stopping, reduce_lr, train_log]
        if 'load local model' in params and os.path.exists(params['model_conf_path'] + '%d.h5' % val_date[0]):
            model.load_weights(params['model_conf_path'] + '%d.h5' % val_date[0])
            print('load model from local')
        else:
            model.fit(train_features, train_label, epochs=params['nb_epoch'], \
                      batch_size=params['batch_size'], verbose=0, \
                      shuffle=True, callbacks=callbacks_list, validation_split=0.05)
            model.save_weights(params['model_conf_path'] + '%d.h5' % val_date[0])
        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            val_features, val_labels = X_train[val_id.values], y_train[val_id.values]
            val_labels = pd.DataFrame(val_labels,index=np.arange(len(val_id))[val_id.values],columns=time_list).stack().to_frame()
            val_labels.columns=['future']
            val_labels['prediction'] = pd.DataFrame(model.predict(val_features),index=np.arange(len(val_id))[val_id.values],columns=time_list).stack()
            pd.to_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % val_date[0])
        if 'train_pred_path' in params:
            if not os.path.exists(params['train_pred_path']):
                os.mkdir(params['train_pred_path'])
            train_label['prediction'] = model.predict(train_features)
            pd.to_pickle(train_label, params['train_pred_path'] + '%d.pkl' % val_date[0])
        return model

        # for cell_num in param['hidden_dim']:
        #     x = SimpleRNN(cell_num,dropout=param['full_conn_dropout'],recurrent_dropout=param['recurrent_dropout'],return_sequences=True)(x)
    def rolling_train_and_predict(self, params={}, period=10, predict_period=10, label_methodology='fix_window', label_param={}, factor_nums=200, kernel=10):
        rolling_train_test_idx_list = self.get_rolling_index(period, predict_period)
        label = pd.DataFrame()#{'actual_label':pd.DataFrame(),'prediction':pd.DataFrame()}
        bar = tqdm(rolling_train_test_idx_list)
        loading_time, training_time, feature_engineering_time, training_sample = 0, 0, 0, 0
        model = None
        fix_factor_list = self.get_fix_factor_evaluation(factor_nums)
        for idx, cell_idx in bar:
            bar.set_description(
                "%s | %d | %d-%d || loading %.1f | feature engineering %.1f | training %.1f | training sample %d" % (
                    datetime.datetime.now().strftime('%H:%M:%S'),
                    os.getpid(), cell_idx[2], cell_idx[3], loading_time, feature_engineering_time,
                    training_time, training_sample))
            train_start_idx, train_end_idx, test_start_idx, test_end_idx = \
                cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3]
            e = time.time()
            print('check', cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3])
            # if test_end_idx!= 20170607:
            #     continue
            X_train, y_train, X_test, y_test,train_index,test_index, feature_engineering_time = \
                self.get_dataset((train_start_idx, train_end_idx), (test_start_idx, test_end_idx),
                                 fix_factor_list, None, label_methodology, label_param, kernel=kernel)
            gc.collect()
            training_sample = X_train.shape[0]
            loading_time = time.time() - e - feature_engineering_time
            e = time.time()
            if len(X_test) == 0:
                print('zero sample')
                continue
            if len(X_train) > 2000 > 1:
                print('re-train in this round')
                model = self.train_model((X_train,train_index), y_train, params, train_end_idx)
            if model is None:
                continue
            training_time = time.time() - e
            pred_label = self.predict(model, X_test, train_end_idx)

            y_test = pd.DataFrame(y_test,index=test_index.index,columns=time_list).stack().to_frame()
            y_test.columns = ['actual_label']
            y_test['prediction'] = pd.DataFrame(pred_label,index=test_index.index,columns=time_list).stack()
            label = label.append(y_test)
            del X_train, y_train, X_test, y_test, pred_label
            gc.collect()
        return label

