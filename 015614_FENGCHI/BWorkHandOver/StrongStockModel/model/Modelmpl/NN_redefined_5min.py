# @Time : 2020/9/29 9:13
# @Author : Zhichen Lu
# @File : NN.py

import pandas as pd
from keras.callbacks import *
from keras.layers import  Dropout, Dense
from keras.losses import mean_squared_error
import keras.backend as K
from keras.optimizers import SGD
from keras.models import Sequential
from sklearn import metrics
import tensorflow as tf
from dataApi.DataPrepare import DataPrepare
from StrongStockModel.conf.path_config import fix_factor_true_send_ic_sort_path
from StrongStockModel.model.ModelBase.ModelBase import ModelBase
import gc

def K_corr(y_true_,y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return (1-K.mean((y_true-K.mean(y_true))*(y_pred-K.mean(y_pred)))/(K.std(y_true)*K.std(y_pred)))


def res_std(y_true_, y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return K.std(y_true - y_pred)


def myloss(y_true_, y_pred_):
    return 0.5 * K_corr(y_true_, y_pred_) + res_std(y_true_, y_pred_)
    # y_true, y_pred = K.cast(y_true_,dtype='float32'),K.cast(y_pred_,dtype='float32')
    # return mean_squared_error(y_pred,y_true) + 2*K_corr(y_true_,y_pred_)

best_param_clf_nn = {
    'activation': 'relu',
    'alpha': 9.756090506594905e-05,
    'hidden_layer_sizes': (16, 32, 8),
    'learning_rate': 'adaptive',
    'learning_rate_init': 0.0703114914234283,
    'momentum': 0.1669382592981298, 'solver': 'sgd',
    'nb_epoch':50,
    'batch_size' : 2**20
}

class NN_redefine(ModelBase):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address='/data/group/800319/JunkSmallFactor/'):
        super().__init__(start, end, stock_pool, feature_address)
        self.dp = DataPrepare(idx_address=feature_address)

    def get_dataset(self, train_idx, test_idx, fix_factor_list, interday_factor, label_method, label_param={}, kernel=10):
        gc.collect()
        e = time.time()
        self.dp.set_date_range(train_idx[0], test_idx[1])
        fix_factor = self.dp.load_data(fix_factor_list + ['future'])
        load_time = time.time() - e
        fix_factor = fix_factor.sort_index()
        train_feature = fix_factor.loc[train_idx[0]:train_idx[-1]]
        train_label = pd.DataFrame(train_feature.pop('future'))
        test_feature = fix_factor.loc[test_idx[0]:test_idx[-1]]
        test_label = pd.DataFrame(test_feature.pop('future'))
        print('load %d ' % (load_time))
        e = time.time()
        train_feature, train_label, test_feature, test_label = \
            self.feature_engineering(train_feature, train_label, test_feature, test_label)
        gc.collect()
        return train_feature, train_label, test_feature, test_label, time.time() - e

    def get_fix_factor_evaluation(self, num):
        ic_res = pd.read_excel('/data/group/800319/FactorEvaluationRes/5min样本内.xlsx', index_col=0).sort_index()
        # ic_res = pd.read_pickle('/data/group/800319/Strong_stock/ic_sort_yearly_avg_window40.pkl').sort_index()
        ic_res.index = ic_res.index.astype(int)
        factor_list = ic_res.loc[1000:2201].sort_values('ic_all_dtc', ascending=False).index.tolist()[:200] + \
                      ic_res.loc[8000:8072].index.tolist() + \
                      ic_res.loc[9500:9599].index.tolist()
        print('factor num %d'%len(factor_list))
        return factor_list#[str(x).zfill(4) for x in range(101,169)]+[str(x).zfill(4) for x in range(9101,9115)]
        # factor_list = [1048, 1018, 1034, 1030, 1076, 1000, 1056, 1029, 1177, 1230, 1145, 1002, 1170, 1333, 1047, 1443, 1012, 1391, 1006, 1090, 451, 1028, 1387, 1105, 1024, 1046,
        #                1054, 1093, 2047, 1340, 1908, 1498, 1045, 1072, 1023, 1760, 1201, 1252, 1338, 1715, 1134, 698, 495, 1249, 1020, 1004, 783, 1016, 1254, 1104, 1142, 1140,
        #                1213, 1231, 516, 462, 1189, 1341, 1125, 1778, 745, 1284, 1208, 419, 1112, 8008, 674, 1182, 1148, 800, 1080, 1976, 1513, 1383, 1010, 1237, 1068, 1099, 579,
        #                1110, 1531, 1268, 2044, 2140, 1075, 1214, 1239, 1960, 1734, 2023, 1172, 1287, 1370, 1153, 1166, 1244, 543, 1292, 1337, 1965, 1139, 1362, 1815, 1281, 805,
        #                1386, 1719, 2200, 2062, 1243, 1260, 1567, 1263, 1920, 1035, 1662, 463, 2177, 1131, 661, 754, 1224, 1167, 1718, 1122, 1059, 1506, 1515, 1152, 1409, 1238,
        #                1480, 1852, 1699, 478, 1686, 1233, 1924, 1156, 1339, 1389, 1225, 547, 1001, 1783, 711, 1083, 1692, 1381, 1304, 537, 1178, 726, 738, 1419, 1814, 1588, 1094,
        #                1932, 2078, 1583, 1352, 1691, 1935, 1679, 1563, 747, 797, 1071, 508, 2035, 2080, 750, 1648, 2153, 1865, 1634, 1609, 2091, 1282]
        # factor_list = [str(x).zfill(4) for x in factor_list]
        # print('factor 180')
        # return factor_list

    def feature_engineering(self, train_feature, train_label, test_feature, test_label):
        value_count = pd.Series((~np.isnan(train_feature.values)).sum(axis=1), index=train_feature.index)
        train_feature = train_feature[value_count > train_feature.shape[1] * 0.80]
        value_count = pd.Series((~np.isnan(test_feature.values)).sum(axis=1), index=test_feature.index)
        test_feature = test_feature[value_count > test_feature.shape[1] * 0.8]
        train_label, test_label = train_label.loc[train_feature.index].dropna(), test_label.loc[
            test_feature.index].dropna()
        train_feature, test_feature = train_feature.loc[train_label.index].fillna(0), test_feature.loc[
            test_label.index].fillna(0)

        train_arr = train_feature.values
        train_arr[train_arr>5] = 5
        train_arr[train_arr < -5] = -5
        train_feature = pd.DataFrame(train_arr,index=train_feature.index,columns=train_feature.columns)
        test_arr = test_feature.values
        test_arr[test_arr> 5] = 5
        test_arr[test_arr <-5] = -5
        test_feature = pd.DataFrame(test_arr,index=test_feature.index,columns=test_feature.columns)
        del train_arr,test_arr
        return train_feature, train_label, test_feature, test_label

    def NN(self,input_dim, params):
        print('CorrOnly')
        hidden_layer_sizes = params['hidden_layer_sizes']
        model = Sequential()
        model.add(Dense(hidden_layer_sizes[0],input_dim=input_dim,activation=params['activation']))
        for dim in hidden_layer_sizes[1:]:
            model.add(Dense(dim,activation=params['activation']))
        model.add(Dense(1))
        optimizer = SGD(lr=params['learning_rate_init'],momentum=params['momentum'])
        self.compile_model(model,optimizer,['mae','mse'])
        # print(model.summary())
        return model

    def compile_model(self, model4compile, opt_er, metrics_eval):
        model4compile.compile(loss=myloss, \
                              optimizer=opt_er, metrics=metrics_eval)
        return model4compile

    def train_model(self, X_train, y_train, params, end_date=None):
        if not os.path.exists(params['train_log_path']):
            os.mkdir(params['train_log_path'])
        if not os.path.exists(params['model_conf_path']):
            os.mkdir(params['model_conf_path'])
        date_list = sorted(list(set([x[0] for x in X_train.index])))
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9]]
        date_list = list(set(date_list) - set(val_date))
        train_features, train_label = X_train.loc[date_list], y_train.loc[date_list]

        model = self.NN(input_dim=X_train.shape[1],params=params)
        early_stopping = EarlyStopping(monitor='val_loss', patience=7)
        reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                                      patience=3, min_lr=0.001)
        train_log = CSVLogger(params['train_log_path']+'%d.csv'%val_date[0])
        callbacks_list = [early_stopping,reduce_lr,train_log]
        if 'load local model' in params and os.path.exists(params['model_conf_path']+'%d.h5'%val_date[0]):
            model.load_weights(params['model_conf_path']+'%d.h5'%val_date[0])
            print('load model from local')
        else:
            model.fit(train_features.values, train_label.values, epochs=params['nb_epoch'], \
                      batch_size=params['batch_size'], verbose=1, \
                      shuffle=True, callbacks=callbacks_list,validation_split=0.05)
            model.save_weights(params['model_conf_path']+'%d.h5'%val_date[0])
        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            val_features, val_labels = X_train.loc[val_date], y_train.loc[val_date]
            val_labels['prediction'] = model.predict(val_features.values)
            pd.to_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % val_date[0])
        if 'train_pred_path' in params:
            if not os.path.exists(params['train_pred_path']):
                os.mkdir(params['train_pred_path'])
            train_label['prediction'] = model.predict(train_features)
            pd.to_pickle(train_label, params['train_pred_path'] + '%d.pkl' % val_date[0])
        return model

    def predict(self, model, X_test,end_date_idx=None):
        pre_label = model.predict(X_test.values)
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
