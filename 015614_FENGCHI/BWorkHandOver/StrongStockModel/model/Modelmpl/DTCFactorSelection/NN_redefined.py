# @Time : 2020/9/29 9:13
# @Author : Zhichen Lu
# @File : NN.py

import pandas as pd
from keras.callbacks import *
from keras.layers import Dropout, Dense
import keras.backend as K
from keras.optimizers import SGD
from keras.models import Sequential
from sklearn import metrics
import tensorflow as tf
from conf.path_config import root_path
from StrongStockModel.model.ModelBase.ModelBase import ModelBase


def K_corr(y_true_, y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return (1 - K.mean((y_true - K.mean(y_true)) * (y_pred - K.mean(y_pred))) / (K.std(y_true) * K.std(y_pred)))


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
    'nb_epoch': 50,
    'batch_size': 2 ** 17
}


class NN_redefine(ModelBase):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None):
        super().__init__(start, end, stock_pool, feature_address)
        self.eval_indicator = factor_eval_indicator
        print(factor_eval_indicator)

    def get_fix_factor_evaluation(self, num):
        if self.eval_indicator == 'intersection':
            return self.get_fix_factor_evaluation_intersection(num)
        elif self.eval_indicator == 'union':
            return self.get_fix_factor_evaluation_union(num)
        elif self.eval_indicator == 'std_adjusted':
            return self.get_factor_std()
        sample = pd.read_hdf(self.feature_address + '20150309.h5', '20150309')
        factor_evaluation = pd.read_excel(root_path + '/external_data/Fix样本内.xlsx', index_col=0)
        inter_col = list(set(factor_evaluation.index).intersection(set(sample.columns)))
        factor_list = factor_evaluation.loc[inter_col, self.eval_indicator].apply(abs).sort_values(ascending=False).index.tolist()[:num]
        return factor_list

    def get_factor_std(self):
        sample = pd.read_hdf(self.feature_address + '20150309.h5', '20150309')
        factor_eval_path = '/data/group/800319/FixFactorTestResult/'
        eval_res_list = os.listdir(factor_eval_path)
        eval_res_list = list(set(eval_res_list).intersection(set(sample.columns)))
        barly_ret = []
        for each in eval_res_list:
            temp_res = pd.read_pickle(factor_eval_path + each)
            barly_ret.append([each] + temp_res['dc_t_all_ret'].tolist())
        check = pd.DataFrame(barly_ret).set_index(0)
        check['std'], check['mean'] = check.std(axis=1), check.mean(axis=1)
        check['adjusted_std'] = (check['std'] / check['mean']).apply(abs)
        factor_evaluation = pd.read_excel(root_path + '/external_data/Fix样本内.xlsx', index_col=0)
        check[['ic_all_t', 'ic_all_d', 'ic_all_c', 'ic_all_dtc']] = abs(factor_evaluation[['ic_all_t', 'ic_all_d', 'ic_all_c', 'ic_all_dtc']])
        check['t_to_std'] = check['ic_all_t'] / check['adjusted_std']
        check['c_to_std'] = check['ic_all_c'] / check['adjusted_std']
        check['d_to_std'] = check['ic_all_d'] / check['adjusted_std']
        check['score'] = check[['t_to_std', 'c_to_std', 'd_to_std']].mean(axis=1)

        selected = check.sort_values('score', ascending=False)[:500]
        selected = selected[((selected['ic_all_t'] > check['ic_all_t'].quantile(0.8)) +
                             (selected['ic_all_c'] > check['ic_all_c'].quantile(0.8)) +
                             (selected['ic_all_d'] > check['ic_all_d'].quantile(0.8))) > 0]
        return selected.index.tolist()

    def get_fix_factor_evaluation_union(self,num):
        sample = pd.read_hdf(self.feature_address + '20150309.h5', '20150309')
        factor_evaluation = pd.read_excel(root_path + '/external_data/Fix样本内.xlsx', index_col=0)
        inter_col = list(set(factor_evaluation.index).intersection(set(sample.columns)))
        for individual_num in range(10,num+1):
            factor_list = {}
            for eval_indicator in ['ic_all_t', 'ic_all_c', 'ic_all_d']:
                factor_list[eval_indicator] = factor_evaluation.loc[inter_col, eval_indicator].apply(abs).sort_values(ascending=False).index.tolist()[:individual_num]
            factor_set = set(factor_list['ic_all_t']).union(set(factor_list['ic_all_c'])).union(set(factor_list['ic_all_d']))
            factor_num = len(factor_set)
            if factor_num>=num:
                print('factor_num',factor_num)
                break
        return list(factor_set)

    def get_fix_factor_evaluation_intersection(self,num):
        sample = pd.read_hdf(self.feature_address + '20150309.h5', '20150309')
        factor_evaluation = pd.read_excel(root_path + '/external_data/Fix样本内.xlsx', index_col=0)
        inter_col = list(set(factor_evaluation.index).intersection(set(sample.columns)))
        for individual_num in range(num,num*2):
            factor_list = {}
            for eval_indicator in ['ic_all_t', 'ic_all_c', 'ic_all_d']:
                factor_list[eval_indicator] = factor_evaluation.loc[inter_col, eval_indicator].apply(abs).sort_values(ascending=False).index.tolist()[:individual_num]
            factor_set = set(factor_list['ic_all_t']).intersection(set(factor_list['ic_all_c'])).intersection(set(factor_list['ic_all_d']))
            factor_num = len(factor_set)
            if factor_num>=num:
                print('factor_num',factor_num)
                break
        return list(factor_set)


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
        train_arr[train_arr > 5] = 5
        train_arr[train_arr < -5] = -5
        train_feature = pd.DataFrame(train_arr, index=train_feature.index, columns=train_feature.columns)
        test_arr = test_feature.values
        test_arr[test_arr > 5] = 5
        test_arr[test_arr < -5] = -5
        test_feature = pd.DataFrame(test_arr, index=test_feature.index, columns=test_feature.columns)
        del train_arr, test_arr
        return train_feature, train_label, test_feature, test_label

    def NN(self, input_dim, params):
        print('CorrOnly')
        hidden_layer_sizes = params['hidden_layer_sizes']
        model = Sequential()
        model.add(Dense(hidden_layer_sizes[0], input_dim=input_dim, activation=params['activation']))
        for dim in hidden_layer_sizes[1:]:
            model.add(Dense(dim, activation=params['activation']))
        model.add(Dense(1))
        optimizer = SGD(lr=params['learning_rate_init'], momentum=params['momentum'])
        self.compile_model(model, optimizer, ['mae', 'mse'])
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

        model = self.NN(input_dim=X_train.shape[1], params=params)
        early_stopping = EarlyStopping(monitor='val_loss', patience=7)
        reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                                      patience=3, min_lr=0.001)
        train_log = CSVLogger(params['train_log_path'] + '%d.csv' % val_date[0])
        callbacks_list = [early_stopping, reduce_lr, train_log]
        if 'load local model' in params and os.path.exists(params['model_conf_path'] + '%d.h5' % val_date[0]):
            model.load_weights(params['model_conf_path'] + '%d.h5' % val_date[0])
            print('load model from local')
        else:
            model.fit(train_features.values, train_label.values, epochs=params['nb_epoch'], \
                      batch_size=params['batch_size'], verbose=0, \
                      shuffle=True, callbacks=callbacks_list, validation_split=0.05)
            model.save_weights(params['model_conf_path'] + '%d.h5' % val_date[0])
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

    def predict(self, model, X_test, end_date_idx=None):
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
