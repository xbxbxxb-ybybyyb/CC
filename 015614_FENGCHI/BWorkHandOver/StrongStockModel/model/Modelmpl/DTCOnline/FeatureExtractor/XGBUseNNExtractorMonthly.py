# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
from xgboost import XGBRegressor
import xgboost as xgb
import os, gc, time, datetime
from StrongStockModel.model.ModelBase.ModelNewLoading import ModelNewLoading
from StrongStockModel.conf.model_param_config import best_param_clf_xgb
from StrongStockModel.conf.path_config import root_path
from dataApi.tradeDate import get_date_range
from tqdm import tqdm
import numpy as np
from dataApi.tradeDate import get_recent_trade_date,get_pre_trade_date
from dataApi.FixFactorRollPrepare import load_fix_data, feature_engineering


from tensorflow.python.keras.callbacks import *
from tensorflow.python.keras.layers import Dropout, Dense,BatchNormalization
import keras.backend as K
from tensorflow.python.keras.optimizers import SGD
from tensorflow.python.keras.models import Sequential
import tensorflow as tf

def K_corr(y_true_, y_pred_):
    y_true, y_pred = K.cast(y_true_, dtype='float32'), K.cast(y_pred_, dtype='float32')
    return K.mean((y_true - K.mean(y_true,axis=0))*(y_pred-K.mean(y_pred,axis=0)),axis=0)/( K.std(y_true,axis=0) * K.std(y_pred,axis=0))

def myloss(y_true_, y_pred_):

    corr = K_corr(y_true_, y_pred_)
    mean_corr = K.mean(corr)
    # std_corr = K.std(corr)
    return 1 - mean_corr#+std_corr


best_param_clf_nn = {
    'activation': 'sigmoid',
    'alpha': 9.756090506594905e-05,
    'hidden_layer_sizes': (200,100),
    'learning_rate': 'adaptive',
    'learning_rate_init': 0.2,#0.0703114914234283,
    'momentum': 0.5, 'solver': 'sgd',
    'nb_epoch': 200,
    'batch_size': 2 ** 19
}

class XGBRegressionFactorEvalYearly(ModelNewLoading):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None, factor_num=None):
        super().__init__(start, end, stock_pool, feature_address, factor_eval_indicator, factor_num=factor_num)

    def NN(self, input_dim, params):
        print('CorrOnly')
        hidden_layer_sizes = params['hidden_layer_sizes']
        model = Sequential()
        model.add(Dense(hidden_layer_sizes[0], input_dim=input_dim, activation=params['activation']))
        model.add(BatchNormalization(momentum=0.5))
        for dim in hidden_layer_sizes[1:]:
            model.add(Dense(dim, activation=params['activation']))
        optimizer = SGD(lr=params['learning_rate_init'], momentum=params['momentum'])
        self.compile_model(model, optimizer, [])
        # print(model.summary())
        return model

    def compile_model(self, model4compile, opt_er, metrics_eval):
        model4compile.compile(loss=myloss, \
                              optimizer=opt_er, metrics=metrics_eval)
        return model4compile


    def get_dataset(self, train_idx, test_idx, fix_factor_list, interday_factor, label_method, label_param={}, kernel=10):
        # self.dp = FixFactorRollPrepare(start_date=train_idx[0], end_date=test_idx[-1], freq=7, model_time_len=1, factor_list=fix_factor_list,
        #                                load_address=self.feature_address)
        gc.collect()
        e = time.time()
        factor_direction = pd.read_pickle('/data/group/800442/800319/strategy_local_path/factor_direction.pkl')[fix_factor_list].values

        # train_feature, train_label = pd.DataFrame(train_feature, index=index_train, columns=fix_factor_list), pd.DataFrame({'actual_label': train_label}, index=index_train)
        train_feature, train_label = pd.read_pickle(label_param['NN_Extracted_Feature_path']+f'{train_idx[-1]}.pkl')
        today = int(datetime.date.today().strftime('%Y%m%d'))
        today = get_recent_trade_date(today)
        if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
            test_feature, test_label = pd.DataFrame(columns=fix_factor_list), pd.DataFrame(columns=fix_factor_list)
        else:
            if test_idx[-1] >= today:
                test_feature, test_label, test_nolimit, test_idx_date, test_idx_code, test_idx_time = load_fix_data(start_date=test_idx[0], end_date=get_pre_trade_date(today),
                                                                                                                    factor_list=fix_factor_list, return_idx=True)
            else:
                test_feature, test_label, test_nolimit, test_idx_date, test_idx_code, test_idx_time = load_fix_data(start_date=test_idx[0], end_date=test_idx[-1],
                                                                                                                    factor_list=fix_factor_list, return_idx=True)
            # test_label = np.concatenate((test_label, np.zeros((test_feature.shape[1] - test_label.shape[0], 7))))
            test_nolimit[np.isnan(test_label)] = True
            test_label[np.isnan(test_label)] = 0
            # test_nolimit = np.concatenate((test_nolimit, np.ones((test_feature.shape[1] - test_nolimit.shape[0], 7)) > 0))
            test_feature, test_label, test_idx_date, test_idx_time, test_idx_code = feature_engineering(test_feature, test_label, test_nolimit, test_idx_date,
                                                                                                        test_idx_time,
                                                                                                        test_idx_code)

            test_feature = test_feature * factor_direction
            index_test = pd.MultiIndex.from_tuples(list(zip(test_idx_date.tolist(), test_idx_time.tolist(), test_idx_code.tolist())))

            test_feature, test_label = pd.DataFrame(test_feature, index=index_test, columns=fix_factor_list), pd.DataFrame({'actual_label': test_label}, index=index_test)
        return train_feature, train_label, test_feature, test_label, time.time() - e

    def get_fix_factor_evaluation(self, num, end_index):
        factor_evaluation = pd.read_pickle(f'{root_path}external_data/moon_v2/{self.eval_indicator}.pkl')
        inter_col = list(set(factor_evaluation.columns.tolist()).intersection(set(self.using_factor_list)))
        factor_evaluation = factor_evaluation[inter_col]
        target_date = max(list(filter(lambda x : x<end_index,factor_evaluation.index.tolist())))
        if 'ret' in self.eval_indicator:
            print('ret')
            factor_evaluation = factor_evaluation.loc[target_date].sort_values(ascending=False)
        elif 'ic' in self.eval_indicator:
            print('ic')
            factor_evaluation = factor_evaluation.loc[target_date].apply(abs).sort_values(ascending=False)
        else:
            raise Exception('')
        factor_list = factor_evaluation.index.tolist()[:num]
        return sorted(factor_list)

    def predict(self, model, X_test, end_date=None,label_param={}):
        NN_model = self.NN(input_dim=X_test.shape[1], params=best_param_clf_nn)
        NN_model.load_weights(label_param['model_conf_path_NN'] + f'{end_date}.h5')
        X_test = pd.DataFrame(NN_model.predict(X_test.values),index=X_test.index)
        dtest = xgb.DMatrix(X_test)
        model.set_param('predictor','cpu_predictor')
        pre_label = model.predict(dtest)
        return pre_label

    def train_model(self, X_train, y_train, params, end_date=None):
        key_list = set(params.keys()).intersection(
            set(['booster', 'colsample_bytree', 'gamma', 'max_depth', 'min_child_weight', 'n_estimators', 'sampling_method', 'subsample', 'tree_method']))
        args_param = {x: params[x] for x in key_list}
        train_end = sorted(list(set([x[0] for x in X_train.index])))[-1]

        print(args_param)
        date_list = get_date_range(X_train.index[0][0], end_date)
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9, -11]]

        date_list = list(set(date_list) - set(val_date))

        factor_list = X_train.columns.tolist()
        pd.to_pickle(factor_list, params['feature_path'] + '%d.pkl' % end_date)

        if 'load local model' in params and os.path.exists(params['model_conf_path'] + '%d.json' % end_date):
            model = xgb.Booster(args_param)
            model.load_model(params['model_conf_path'] + '%d.json' % end_date)
            print('load from local', end_date)
            # return model
        else:
            print('no exist model conf')
            if not os.path.exists(params['model_conf_path']):
                os.mkdir(params['model_conf_path'])
            ########################
            train_features, train_label = X_train.loc[date_list], y_train.loc[date_list]
            d_train = xgb.DMatrix(train_features[:-50000], label=train_label[:-50000].values)
            d_eval = xgb.DMatrix(train_features[-50000:], label=train_label[-50000:].values)
            model = xgb.train(args_param, d_train, num_boost_round=params['n_estimators'], evals=[(d_eval, 'd_eval')], early_stopping_rounds=15, verbose_eval=True)
            model.save_model(params['model_conf_path'] + '%d.json' % end_date)
            print(params['model_conf_path'] + '%d.json' % end_date)

        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            val_features, val_labels = X_train.loc[val_date[1:]], y_train.loc[val_date[1:]]
            d_val = xgb.DMatrix(val_features)
            val_labels['prediction'] = model.predict(d_val)
            pd.to_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % end_date)
        if 'train_pred_path' in params:
            if not os.path.exists(params['train_pred_path']):
                os.mkdir(params['train_pred_path'])
            train_label['prediction'] = model.predict(d_train)
            pd.to_pickle(train_label, params['train_pred_path'] + '%d.pkl' % end_date)
        return model

    def rolling_train_and_predict(self, params={}, period=10, predict_period=10, label_methodology='fix_window', label_param={}, factor_nums=200, kernel=10):
        rolling_train_test_idx_list = self.get_rolling_index(period, predict_period)
        label = pd.DataFrame()
        bar = tqdm(rolling_train_test_idx_list)
        loading_time, training_time, feature_engineering_time, training_sample = 0, 0, 0, 0
        model = None

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
            fix_factor_list = pd.read_pickle(params['feature_path_NN']+f'{train_end_idx}.pkl')#self.get_fix_factor_evaluation(factor_nums, train_end_idx)
            X_train, y_train, X_test, y_test, feature_engineering_time = \
                self.get_dataset((train_start_idx, train_end_idx), (test_start_idx, test_end_idx),
                                 fix_factor_list, None, label_methodology, params, kernel=kernel)
            gc.collect()
            training_sample = X_train.shape[0]
            loading_time = time.time() - e - feature_engineering_time
            e = time.time()

            if len(X_train) > 2000 and len(set(y_train[y_train.columns[0]])) > 1:
                print('re-train in this round')
                model = self.train_model(X_train, y_train, params, train_end_idx)
            if model is None:
                continue
            training_time = time.time() - e
            if len(X_test) == 0:
                print('zero sample')
                continue
            else:
                pred_label = self.predict(model, X_test, train_end_idx,params)
                y_test.columns = ['actual_label']
                y_test['prediction'] = pred_label
                print('test_ic', train_end_idx, y_test.corr())
                label = label.append(y_test)
                del X_train, y_train, X_test, y_test, pred_label
                gc.collect()
        return label


from xquant.xqutils.helper import link
import configparser

conf = configparser.ConfigParser()
conf.read('/data/group/800442/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])


def main_window_search(i, indicator):
    train_period = 200
    test_period = 10
    factor_num = 800

    tag = 'XGBUseNNExtractorV2_%s_train%d_test%d_factor_num%d' % (indicator, train_period, test_period, factor_num)
    out_file = f'/data/group/800442/800319/Strong_stock/C3PO/{tag}/{tag}.pkl'

    tag_NN = 'NNExtractor_%s_train%d_test%d_factor_num%d' % (indicator, 100, 200, 800)
    out_file_NN = f'/data/group/800442/800319/Strong_stock/C3PO/{tag_NN}/{tag_NN}.pkl'


    base_dir = out_file.replace('.pkl', '/')
    train_start, train_end, test_start, test_end = para_list[i][1]
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    if os.path.exists(base_dir + '%d.pkl' % train_end):
        print(train_end, 'exist')
        return
    print(out_file)

    best_param_clf_xgb = { 'n_estimators': 100,'subsample': 0.8, 'tree_method': 'gpu_hist'}
    best_param_clf_xgb['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    best_param_clf_xgb['model_conf_path'] = out_file.replace('.pkl', '_model_conf/')
    best_param_clf_xgb['feature_path'] = out_file.replace('.pkl', '_factor_list/')

    # best_param_clf_xgb['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    best_param_clf_xgb['model_conf_path_NN'] = out_file_NN.replace('.pkl', '_model_conf/')
    best_param_clf_xgb['feature_path_NN'] = out_file_NN.replace('.pkl', '_feature_path/')
    best_param_clf_xgb['NN_Extracted_Feature_path'] = out_file_NN.replace('.pkl', '/')


    model = XGBRegressionFactorEvalYearly(train_start, test_end, None, feature_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/',
                                          factor_eval_indicator=indicator,
                                          factor_num=factor_num)
    if not os.path.exists(best_param_clf_xgb['model_conf_path']):
        os.mkdir(best_param_clf_xgb['model_conf_path'])
    if not os.path.exists(best_param_clf_xgb['feature_path']):
        os.mkdir(best_param_clf_xgb['feature_path'])
    best_param_clf_xgb['load local model'] = True
    label = model.rolling_train_and_predict(params=best_param_clf_xgb, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=15, factor_nums=factor_num)
    pd.to_pickle(label, base_dir + '%d.pkl' % train_end)
    print(base_dir + '%d.pkl' % train_end)

from multiprocessing import Process

idx_list = list(range(24,133))
for i in tqdm(idx_list):
    for ind_name in ['ic_d']:
    # for ind_name in ['top_ret'][::-1]:
        pro = Process(target=main_window_search,args=(i, ind_name))
        # main_window_search(i, ind_name)
        pro.start()
        pro.join()
        del pro


for i in tqdm(idx_list):
    for ind_name in ['ic_t']:
    # for ind_name in ['top_ret'][::-1]:
        pro = Process(target=main_window_search,args=(i, ind_name))
        # main_window_search(i, ind_name)
        pro.start()
        pro.join()
        del pro

for i in tqdm(idx_list):
    for ind_name in ['ic_c']:
    # for ind_name in ['top_ret'][::-1]:
        pro = Process(target=main_window_search,args=(i, ind_name))
        # main_window_search(i, ind_name)
        pro.start()
        pro.join()
        del pro