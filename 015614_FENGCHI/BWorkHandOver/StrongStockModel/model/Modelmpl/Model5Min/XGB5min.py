# @Time : 2021/6/22 9:15
# @Author : Zhichen Lu
# @File : XGB5min.py


# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression.py
import numpy as np
import pandas as pd
from sklearn import metrics
from xgboost import XGBRegressor
import xgboost as xgb
import os
from StrongStockModel.model.ModelBase.ModelBase import ModelBase
from StrongStockModel.model.Modelmpl.Model5Min.BaseModel5M import Factor5MinLoader
from StrongStockModel.conf.path_config import root_path
import datetime, time, gc
from tqdm import tqdm



class XGB5min(ModelBase):
    def __init__(self, start=20170103, end=20191231,factor_num=100, stock_pool=None, feature_address='/data/group/800319/HFfactor/DTC2021/data/',indicator=None):
        super().__init__(start, end, stock_pool, feature_address)
        self.indicator = indicator
        eval_res = pd.read_excel('/data/group/800319/HFfactor/DTC1210/result/factor1231_nolimit.xlsx').set_index('name')
        exist_factor_list = os.listdir('/data/group/800319/HFfactor/DTC2021/data/')
        inter_factor = [int(x) for x in set([x.replace('.npy','') for x in exist_factor_list]).intersection(set(eval_res.index.astype(str)))]
        self.eval_res = pd.read_pickle(f'/data/group/800319/junkData/StrongStock/external_data/factor5min_eval/{indicator}.pkl')
        self.factor_num = factor_num
        self.feature_address = feature_address
        if 'ic' in indicator:
            self.eval_res = abs(self.eval_res)


    def get_dataset(self, train_idx, test_idx, fix_factor_list, interday_factor, label_method, label_param={}, kernel=10):

        e = time.time()
        train_start, train_end = train_idx
        predict_start, predict_end = test_idx
        test_date_idx = [-1, -3, -5, -7, -9]

        target_date = max(list(filter(lambda x : x<train_end,self.eval_res.index)))
        print(f'target day of {train_end} is {target_date}')
        self.factor_list = self.eval_res.loc[target_date].apply(abs).sort_values(ascending=False).index.to_list()[:self.factor_num]
        self.loader = Factor5MinLoader(
            start_date=train_start,
            end_date=predict_end,
            freq=48,
            factor_list=self.factor_list,
            load_address=self.feature_address)
        X_train, y_train,d_train,t_train,c_train, X_test, y_test, d_test, t_test, c_test, X_pred, y_pred, d_pred, t_pred, c_pred = \
            self.loader.lazy_reach_data(train_start, train_end, predict_start, predict_end, test_date_idx, limit=0.2)
        index_test = pd.MultiIndex.from_tuples(list(zip(d_pred, t_pred, c_pred)))
        y_pred = pd.DataFrame({'actual_label':y_pred},index=index_test)
        return (X_train,X_test), (y_train,y_test), X_pred, y_pred, time.time() - e

    def predict(self, model, X_test, end_date=None):
        dtest = xgb.DMatrix(X_test)
        pre_label = model.predict(dtest)
        return pre_label

    def train_model(self, X, y, params, end_date=None):
        train_features,val_features = X
        train_label, val_labels = y

        key_list = set(params.keys()).intersection(
            set(['booster', 'colsample_bytree', 'gamma', 'max_depth', 'min_child_weight', 'n_estimators', 'sampling_method', 'subsample', 'tree_method']))
        args_param = {x: params[x] for x in key_list}
        print(args_param)
        pd.to_pickle(self.factor_list, params['feature_path'] + '%d.pkl' % end_date)

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
            d_train = xgb.DMatrix(train_features[:-50000], label=train_label[:-50000])
            d_eval = xgb.DMatrix(train_features[-50000:], label=train_label[-50000:])
            model = xgb.train(args_param, d_train, num_boost_round=params['n_estimators'], evals=[(d_eval, 'd_eval')], early_stopping_rounds=15, verbose_eval=False)
            model.save_model(params['model_conf_path'] + '%d.json' % end_date)
            print(params['model_conf_path'] + '%d.json' % end_date)
        model.set_param('predictor','cpu_predictor')
        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            d_val = xgb.DMatrix(val_features)
            val_labels = pd.DataFrame({'actual_label':val_labels,'prediction':model.predict(d_val)})
            pd.to_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % end_date)
        return model


from xquant.xqutils.helper import link
import configparser

conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])


def main_window_search(i, indicator):
    train_period = 200
    test_period = 10
    factor_num = 100
    tag = f'XGB5min_{indicator}_train{train_period}_test{test_period}_factor_num{factor_num}'
    if not os.path.exists(f'{root_path}/ModelRes/{tag}/'):
        os.mkdir(f'{root_path}/ModelRes/{tag}/')
    out_file = f'{root_path}/ModelRes/{tag}/{tag}.pkl'
    base_dir = out_file.replace('.pkl', '/')
    train_start, train_end, test_start, test_end = para_list[i][1]
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    if os.path.exists(base_dir + '%d.pkl' % train_end):
        print(train_end, 'exist')
        return
    print(out_file)

    best_param_clf_xgb = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607,
                          'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100, 'sampling_method': 'gradient_based',
                          'subsample': 0.8, 'tree_method': 'gpu_hist'}
    best_param_clf_xgb['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    best_param_clf_xgb['model_conf_path'] = out_file.replace('.pkl', '_model_conf/')
    best_param_clf_xgb['feature_path'] = out_file.replace('.pkl', '_factor_list/')
    model = XGB5min(train_start, test_end,
                                          indicator=indicator,
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

 # ['ic_half_d', 'ic_half_t', 'ic_half_c', 't_dc_half_ret', 'dc_t_half_ret', 'dt_c_half_ret']
for i in tqdm(list(range(133))):
    for ind_name in [ 't_dc_half_ret', 'dc_t_half_ret', 'dt_c_half_ret']:
        main_window_search(i, ind_name)
        gc.collect()