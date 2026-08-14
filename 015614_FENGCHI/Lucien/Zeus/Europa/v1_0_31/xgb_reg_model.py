# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 8:47
import sys
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import numpy as np
from Zeus.Europa.v1_0_31.path_conf import *
from Zeus.Europa.v1_0_31.hyper_param_space import hyper_xgb_reg_params
from Zeus.BTLite.BTLite import BTLite
from xgboost import XGBRegressor
from LucienUtil.FileUtil import FileUtil
from Zeus.Europa.v1_0_31.my_logger import MyLogger
import warnings
import os
import time
np.random.seed(2024)
warnings.filterwarnings("ignore")

PERIOD = 'period5'
SUB_VERSION = 'v5'

# 开始正式训练
hyper_search_mode = False
fit_cheat_mode = False
use_test_param_mode = False

# param_test ={'booster': 'gbtree', 'colsample_bytree': 0.5, 'factor_num': 2030.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 9.0, 'min_child_weight': 6.0, 'n_estimators': 1200.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.3, 'reg_lambda': 0.0, 'scale_pos_weight': 1.0, 'score_threshold': -0.00180983543395996, 'silent': True, 'subsample': 1.0, 'tree_method': 'gpu_hist'}
# param_fit ={'booster': 'gbtree', 'colsample_bytree': 1.0, 'factor_num': 2030.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 4.0, 'min_child_weight': 2.0, 'n_estimators': 1400.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.5, 'reg_lambda': 0.1, 'scale_pos_weight': 1.0, 'score_threshold': 0.00189709663391113, 'silent': True, 'subsample': 0.7, 'tree_method': 'gpu_hist'}

# param_test ={'booster': 'gbtree', 'colsample_bytree': 1.0, 'factor_num': 2020.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 9.0, 'min_child_weight': 6.0, 'n_estimators': 1500.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.0, 'reg_lambda': 1.0, 'scale_pos_weight': 1.0, 'score_threshold': -0.00062483549118042, 'silent': True, 'subsample': 0.6, 'tree_method': 'gpu_hist'}
# param_fit ={'booster': 'gbtree', 'colsample_bytree': 0.5, 'factor_num': 2030.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 9.0, 'min_child_weight': 6.0, 'n_estimators': 1100.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 1.0, 'reg_lambda': 0.6, 'scale_pos_weight': 1.0, 'score_threshold': 0.00500264763832092, 'silent': True, 'subsample': 0.5, 'tree_method': 'gpu_hist'}

# param_test ={'booster': 'gbtree', 'colsample_bytree': 0.7, 'factor_num': 2030.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 7.0, 'min_child_weight': 2.0, 'n_estimators': 1000.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.6, 'reg_lambda': 0.1, 'scale_pos_weight': 1.0, 'score_threshold': 0.00568893551826477, 'silent': True, 'subsample': 0.6, 'tree_method': 'gpu_hist'}
# param_fit ={'booster': 'gbtree', 'colsample_bytree': 0.7, 'factor_num': 2020.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 4.0, 'min_child_weight': 5.0, 'n_estimators': 1400.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.6, 'reg_lambda': 0.8, 'scale_pos_weight': 1.0, 'score_threshold': 0.00454813241958618, 'silent': True, 'subsample': 0.9, 'tree_method': 'gpu_hist'}

# period4 作废
# param_test = {'booster': 'gbtree', 'colsample_bytree': 1.0, 'factor_num': 2030.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 9.0, 'min_child_weight': 1.0, 'n_estimators': 1100.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.0, 'reg_lambda': 0.5, 'scale_pos_weight': 1.0, 'score_threshold': 0.00483423471450806, 'silent': True, 'subsample': 0.6, 'tree_method': 'gpu_hist'}
# param_fit = {'booster': 'gbtree', 'colsample_bytree': 1.0, 'factor_num': 2030.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 9.0, 'min_child_weight': 1.0, 'n_estimators': 1100.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.0, 'reg_lambda': 0.5, 'scale_pos_weight': 1.0, 'score_threshold': 0.00483423471450806, 'silent': True, 'subsample': 0.6, 'tree_method': 'gpu_hist'}

# param_test = {'booster': 'gbtree', 'colsample_bytree': 0.6, 'factor_num': 2030.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 8.0, 'min_child_weight': 4.0, 'n_estimators': 1300.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.1, 'reg_lambda': 0.9, 'scale_pos_weight': 1.0, 'score_threshold': 0.00481030344963074, 'silent': True, 'subsample': 0.5, 'tree_method': 'gpu_hist'}
# param_fit = {'booster': 'gbtree', 'colsample_bytree': 0.6, 'factor_num': 2030.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 8.0, 'min_child_weight': 4.0, 'n_estimators': 1300.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.1, 'reg_lambda': 0.9, 'scale_pos_weight': 1.0, 'score_threshold': 0.00481030344963074, 'silent': True, 'subsample': 0.5, 'tree_method': 'gpu_hist'}

param_test = {'booster': 'gbtree', 'colsample_bytree': 0.5, 'factor_num': 2030.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 8.0, 'min_child_weight': 3.0, 'n_estimators': 1500.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.2, 'reg_lambda': 1.0, 'scale_pos_weight': 1.0, 'score_threshold': 0.0054384171962738, 'silent': True, 'subsample': 0.8, 'tree_method': 'gpu_hist'}
param_fit = {'booster': 'gbtree', 'colsample_bytree': 0.5, 'factor_num': 2030.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 8.0, 'min_child_weight': 3.0, 'n_estimators': 1500.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.2, 'reg_lambda': 1.0, 'scale_pos_weight': 1.0, 'score_threshold': 0.0054384171962738, 'silent': True, 'subsample': 0.8, 'tree_method': 'gpu_hist'}

hyper_params = hyper_xgb_reg_params

class XgbRegModel:
    def __init__(self, mode='test', sub_version='v1'):
        self.model_name = 'XgbRegModel'
        self.strategy_name = 'Europa'
        self.version = 'v1_0_31'
        self.sub_version = sub_version
        self.prefix_path = f'{self.strategy_name}/{self.version}/{self.model_name}/'

        self.pred_out_path = pred_out_path + self.prefix_path
        self.bt_out_path = bt_out_path + self.prefix_path
        self.factor_path = factor_path + self.prefix_path
        self.log_path = log_path + self.prefix_path
        self.hyper_pred_out_path = None
        self.create_floders()

        self.X, self.y = None, None
        self.mode = mode
        self.model = None
        self.scaler = None
        self.label = 'label_pct_graded'
        self.factor_list = None
        self.search_time = 0
        self.date_dict = date_config[f'{PERIOD}_{mode}']
        self.X_train, self.X_valid, self.X_test, self.y_train, self.y_valid, self.y_test = None, None, None, None, None, None
        self.pred_fname = f'{self.date_dict["test_start_date"]}~{self.date_dict["test_end_date"]}_{self.model_name}_{self.sub_version}.csv'

        self.get_dataset(data_test_fpath_with_label)

    def create_floders(self):
        os.makedirs(self.pred_out_path, exist_ok=True)
        os.makedirs(self.bt_out_path, exist_ok=True)
        os.makedirs(self.factor_path, exist_ok=True)
        os.makedirs(self.log_path, exist_ok=True)

    def get_dataset(self, path):
        samples = pd.read_pickle(path)
        X = samples[filter(lambda x: x.find('label'), samples.columns.tolist())]
        X = X.dropna(how='any', axis=0)
        X = samples.loc[X.index]

        y = pd.read_pickle('/data/group/800463/sunss/for_xly/europa/newProfit/LabelProfit_zt_twap_0.10_800_190_SH300_SZ30.pkl')
        y = y[[self.label]]
        y.columns = [self.label]

        y = y.reindex(index=X.index)

        # # TODO：delete，20220101之后日期的label都赋值成了0
        # y['trade_date'] = y.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
        # y.loc[y['trade_date'] >= 20220101, self.label] = 0

        y = y.drop(np.isnan(y)[self.label][np.isnan(y)[self.label]].index)
        X = X.reindex(index=y.index)

        self.X = X
        self.y = y

    def filter_factor(self, xgb_imptc_fpath=None, factor_score_fpath=factor_score_fpath):
        factor_list = self.fun_filter_factor1(xgb_imptc_fpath=xgb_imptc_fpath, factor_score_fpath=factor_score_fpath)
        return factor_list

    def fun_filter_factor1(self, xgb_imptc_fpath=None, factor_score_fpath=None):
        filter_factor_df = pd.read_excel(xgb_imptc_fpath, index_col=0)
        _xgb_imptc_factor = filter_factor_df.query('corr_selected==1')
        factor_list = _xgb_imptc_factor['factor_name'].tolist()
        print(f'use {len(factor_list)} factors')

        self.factor_list = factor_list
        return factor_list

    def fun_filter_factor2(self, xgb_imptc_fpath=None, factor_score_fpath=None):
        filter_factor_df = pd.read_excel(factor_score_fpath, index_col=0)
        _xgb_imptc_factor = filter_factor_df.query('low_cost==1')
        factor_list = _xgb_imptc_factor['factor_name'].tolist()

        self.factor_list = factor_list
        return factor_list

    def fun_filter_factor3(self, xgb_imptc_fpath=None, factor_score_fpath=None):
        filter_factor_df = pd.read_excel(xgb_imptc_fpath, index_col=0)
        _xgb_imptc_factor = filter_factor_df.sort_values('feature_importance_rank_mean')
        _xgb_imptc_factor = _xgb_imptc_factor.query('feature_importance_rank_mean < 320')
        _xgb_imptc_factor = _xgb_imptc_factor.sort_values('feature_importance_rank_std', ascending=True)
        factor_list = _xgb_imptc_factor['factor_name'].tolist()[:220]
        print(f'use {len(factor_list)} factors')

        self.factor_list = factor_list
        return factor_list

    def get_train_and_test_data(self):
        X_copy = self.X.copy()
        y_copy = self.y.copy()
        X_copy = X_copy.drop(X_copy.filter(regex='label*').columns.tolist(), axis=1)
        y_copy = y_copy.reindex(index=X_copy.index)

        filtered_factor = self.filter_factor(xgb_imptc_fpath=eval(f'xgb_imptc_{PERIOD}_fpath'))
        X_copy = X_copy[filtered_factor]

        X_copy['trade_date'] = X_copy.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
        y_copy['trade_date'] = y_copy.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()

        X_train = X_copy.query(f'trade_date >= {self.date_dict["train_start_date"]} & trade_date <= {self.date_dict["train_end_date"]}')
        y_train = y_copy.query(f'trade_date >= {self.date_dict["train_start_date"]} & trade_date <= {self.date_dict["train_end_date"]}')
        X_valid = X_copy.query(f'trade_date >= {self.date_dict["valid_start_date"]} & trade_date <= {self.date_dict["valid_end_date"]}')
        y_valid = y_copy.query(f'trade_date >= {self.date_dict["valid_start_date"]} & trade_date <= {self.date_dict["valid_end_date"]}')
        X_test = X_copy.query(f'trade_date >= {self.date_dict["test_start_date"]} & trade_date <= {self.date_dict["test_end_date"]}')
        y_test = y_copy.query(f'trade_date >= {self.date_dict["test_start_date"]} & trade_date <= {self.date_dict["test_end_date"]}')

        y_train = y_train[[self.label]]
        y_valid = y_valid[[self.label]]
        y_test = y_test[[self.label]]

        X_train = X_train.drop('trade_date', axis=1)
        X_valid = X_valid.drop('trade_date', axis=1)
        X_test = X_test.drop('trade_date', axis=1)

        # 选择预处理方式
        # X_train, X_valid, X_test = self.fun_trans_train_test_minmaxscaler(X_train, X_valid, X_test)
        X_train, X_valid, X_test = self.fun_trans_train_test_standardscaler(X_train, X_valid, X_test)
        # X_train, X_valid, X_test = self.fun_trans_train_test_minmaxmadscaler(X_train, X_valid, X_test)

        self.X_train, self.X_valid, self.X_test, self.y_train, self.y_valid, self.y_test = X_train, X_valid, X_test, y_train, y_valid, y_test
        return X_train, y_train, X_valid, y_valid, X_test, y_test

    def fun_trans_train_test_minmaxscaler(self, X_train, X_valid, X_test):
        train_data = pd.concat([X_train, X_valid], axis=0).drop_duplicates()
        test_data = X_test

        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        scaler = scaler.fit(train_data)
        X_train_scaled_array = scaler.transform(X_train)
        X_valid_scaled_array = scaler.transform(X_valid)
        X_test_scaled_array = scaler.transform(test_data)

        X_train_scaled = pd.DataFrame(X_train_scaled_array, index=X_train.index, columns=X_train.columns)
        X_valid_scaled = pd.DataFrame(X_valid_scaled_array, index=X_valid.index, columns=X_valid.columns)
        X_test_scaled = pd.DataFrame(X_test_scaled_array, index=X_test.index, columns=X_test.columns)

        self.scaler = scaler
        return X_train_scaled, X_valid_scaled, X_test_scaled

    def fun_trans_train_test_standardscaler(self, X_train, X_valid, X_test):
        train_data = pd.concat([X_train, X_valid], axis=0).drop_duplicates()
        test_data = X_test

        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        scaler = scaler.fit(train_data)
        X_train_scaled_array = scaler.transform(X_train)
        X_valid_scaled_array = scaler.transform(X_valid)
        X_test_scaled_array = scaler.transform(test_data)

        X_train_scaled = pd.DataFrame(X_train_scaled_array, index=X_train.index, columns=X_train.columns)
        X_valid_scaled = pd.DataFrame(X_valid_scaled_array, index=X_valid.index, columns=X_valid.columns)
        X_test_scaled = pd.DataFrame(X_test_scaled_array, index=X_test.index, columns=X_test.columns)

        self.scaler = scaler
        return X_train_scaled, X_valid_scaled, X_test_scaled

    def fun_trans_train_test_minmaxmadscaler(self, X_train, X_valid, X_test):
        train_data = pd.concat([X_train, X_valid], axis=0).drop_duplicates()

        def _fun_median_mad(_arr, n):
            arr = _arr.copy()
            median = np.median(arr, axis=0)
            mad = np.median(np.abs(arr - median), axis=0)
            arr1 = np.where(arr > (median + n * mad), np.repeat((median + n * mad)[None, :], arr.shape[0], 0), arr)
            arr2 = np.where(arr1 < (median - n * mad), np.repeat((median - n * mad)[None, :], arr1.shape[0], 0), arr1)
            return arr2, median, mad

        def _fit_minmax_median_mad(_arr, n=3):
            arr = _arr.copy()
            arr2, median, mad = _fun_median_mad(arr, n)
            data_min = np.min(arr2, axis=0)
            data_max = np.max(arr2, axis=0)
            return n, median, mad, data_min, data_max

        def _trans_train_test_minmaxscaler(_arr, n, median, mad, data_min, data_max):
            arr = _arr.copy()
            arr1 = np.where(arr > (median + n * mad), np.repeat((median + n * mad)[None, :], arr.shape[0], 0), arr)
            arr2 = np.where(arr1 < (median - n * mad), np.repeat((median - n * mad)[None, :], arr1.shape[0], 0), arr1)
            arr_sclaled = (arr2 - data_min) / (data_max - data_min)
            return arr_sclaled

        n, median, mad, train_min, train_max = _fit_minmax_median_mad(train_data.values, n=5)
        X_train_scaled_array = _trans_train_test_minmaxscaler(X_train.values, n, median, mad, train_min, train_max)
        X_valid_scaled_array = _trans_train_test_minmaxscaler(X_valid.values, n, median, mad, train_min, train_max)
        X_test_scaled_array = _trans_train_test_minmaxscaler(X_test.values, n, median, mad, train_min, train_max)

        X_train_scaled = pd.DataFrame(X_train_scaled_array, index=X_train.index, columns=X_train.columns)
        X_valid_scaled = pd.DataFrame(X_valid_scaled_array, index=X_valid.index, columns=X_valid.columns)
        X_test_scaled = pd.DataFrame(X_test_scaled_array, index=X_test.index, columns=X_test.columns)

        self.scaler = (n, median, mad, train_min, train_max)
        return X_train_scaled, X_valid_scaled, X_test_scaled

    def train_model(self, X_train, y_train, param):
        model = XGBRegressor(**param)
        model.fit(X_train.values, y_train.values.ravel())
        self.model = model

        # import xgboost as xgb
        # self.model = xgb.Booster(model_file='/data/group/800463/fengc/for_wj/20230119_europa_period5/XgbRegModel/period5_XgbRegModel.pkl')

        return model

    def predict(self, X_other):
        _y_pred = self.model.predict(X_other)
        return _y_pred

    def tranfrom_pred_data(self, y_valid_pred, y_test_pred, score_threshold=0):
        valid_test_pred = list(np.concatenate([y_valid_pred > score_threshold, y_test_pred > score_threshold]))
        valid_test_pred_prob = list(np.concatenate([y_valid_pred, y_test_pred]))
        valid_test_pred_df = pd.DataFrame(index=self.X_valid.index).append(pd.DataFrame(index=self.X_test.index))
        valid_test_pred_df['prediction'] = valid_test_pred
        valid_test_pred_df['pred_Reg'] = valid_test_pred_prob
        valid_test_pred_df['stockID'] = valid_test_pred_df.index.get_level_values(1)
        valid_test_pred_df['datelist'] = valid_test_pred_df.index.get_level_values(0).strftime('%Y%m%d')
        valid_test_pred_df['Indexs'] = valid_test_pred_df['stockID'] + ' ' + valid_test_pred_df['datelist']
        valid_test_pred_df = valid_test_pred_df.set_index('Indexs', drop=True)
        return valid_test_pred_df

    def start_train(self, param):
        param_copy = param.copy()
        if 'n_estimators' in param_copy.keys():
            param_copy['n_estimators'] = int(param_copy['n_estimators'])
        if 'factor_num' in param_copy.keys():
            param_copy['factor_num'] = int(param_copy['factor_num'])
        if 'max_depth' in param_copy.keys():
            param_copy['max_depth'] = int(param_copy['max_depth'])

        score_threshold = 0
        factor_num = 1000
        if 'factor_num' in param_copy.keys():
            factor_num = int(param_copy.pop('factor_num'))
        if 'score_threshold' in param_copy.keys():
            score_threshold = param_copy.pop('score_threshold')

        X_train, y_train, X_valid, y_valid, X_test, y_test = self.get_train_and_test_data()
        self.train_model(X_train, y_train, param=param_copy)
        y_valid_pred = self.predict(X_valid.values)
        y_test_pred = self.predict(X_test.values)
        valid_test_pred_df = self.tranfrom_pred_data(y_valid_pred, y_test_pred, score_threshold=score_threshold)
        return valid_test_pred_df


inst_test = XgbRegModel(mode='test', sub_version=SUB_VERSION)
inst_fit = XgbRegModel(mode='fit', sub_version=SUB_VERSION)

if hyper_search_mode or use_test_param_mode:
    my_logger = MyLogger(strategy_name=inst_test.strategy_name, model_name=inst_test.model_name, version=inst_test.version, sub_version=inst_test.sub_version).get_logger()
    my_logger.info(f'{inst_test.strategy_name} {inst_test.version} {inst_test.model_name} {inst_test.sub_version}')
else:
    my_logger = None

btl_test = BTLite(valid_fpath=None,
                  test_fpath=None,
                  strategy_name='Europa',
                  model_name='SingleTestModel',
                  date_dict=date_config[f'{PERIOD}_test'],
                  bt_save_path=junk_path + '回测结果/')
btl_fit = BTLite(valid_fpath=None,
                 test_fpath=None,
                 strategy_name='Europa',
                 model_name='SingleTestModel',
                 date_dict=date_config[f'{PERIOD}_fit'],
                 bt_save_path=junk_path + '回测结果/')

def tuning_params(param):
    param['colsample_bytree'] = round(param['colsample_bytree'], 1)
    param['reg_alpha'] = round(param['reg_alpha'], 1)
    param['reg_lambda'] = round(param['reg_lambda'], 1)
    param['subsample'] = round(param['subsample'], 1)

    pred_result = inst_test.start_train(param=param)
    inst_test.hyper_pred_out_path = inst_test.pred_out_path + f'hyper/{inst_test.search_time}/'
    FileUtil.save_df2csv(pred_result, inst_test.hyper_pred_out_path, inst_test.pred_fname)

    btl_test.set_valid_fpath(inst_test.hyper_pred_out_path + inst_test.pred_fname)
    btl_test.set_test_fpath(inst_test.hyper_pred_out_path + inst_test.pred_fname)
    btl_test.set_bt_save_path(inst_test.hyper_pred_out_path)

    model_eval, model_valid_mingan, model_test_mingan = btl_test.start_backtest()
    model_valid_mingan = model_valid_mingan.sort_values('收益风险比', ascending=False)
    model_valid_mingan['test_indicator'] = model_valid_mingan['收益风险比'] * model_valid_mingan['累计盈利']
    model_valid_mingan_copy = model_valid_mingan.copy()
    model_valid_mingan_copy['fit_indicator'] = model_valid_mingan_copy['收益风险比'] * model_valid_mingan_copy['扣费收益率胜率'] * model_valid_mingan_copy['实际参与率']
    model_valid_mingan_copy = model_valid_mingan_copy.query('0.2 < 实际参与率 < 0.4')
    model_valid_mingan_copy = model_valid_mingan_copy.sort_values(['fit_indicator'], ascending=False).iloc[0]
    in_adapt_score_threshold = model_valid_mingan_copy.name
    model_test_mingan_copy_ = model_test_mingan.loc[in_adapt_score_threshold]

    model_test_mingan = model_test_mingan.sort_values('收益风险比', ascending=False)
    model_test_mingan['test_indicator'] = model_test_mingan['收益风险比'] * model_test_mingan['累计盈利']
    model_test_mingan_copy = model_test_mingan.copy()
    model_test_mingan_copy['fit_indicator'] = model_test_mingan_copy['收益风险比'] * model_test_mingan_copy['扣费收益率胜率'] * model_test_mingan_copy['实际参与率']
    model_test_mingan_copy = model_test_mingan_copy.query('0.2 < 实际参与率 < 0.4')
    model_test_mingan_copy = model_test_mingan_copy.sort_values(['fit_indicator'], ascending=False).iloc[0]

    ic = round(model_eval['预测值与标签RankIC'], 4) if model_eval.shape[0] > 0 else 0
    adapt_profit_risk_ratio = round(model_test_mingan_copy['收益风险比'], 4) if model_test_mingan_copy.shape[0] > 0 else 0
    adapt_winrate = round(model_test_mingan_copy['扣费收益率胜率'], 4) if model_test_mingan_copy.shape[0] > 0 else 0
    adapt_join_pct = round(model_test_mingan_copy['实际参与率'], 4) if model_test_mingan_copy.shape[0] > 0 else 0
    adapt_sharpe_ratio = round(model_test_mingan_copy['夏普比率'], 4) if model_test_mingan_copy.shape[0] > 0 else 0
    adapt_cum_profit = round(model_test_mingan_copy['累计盈利'], 4) if model_test_mingan_copy.shape[0] > 0 else 0
    adapt_score_threshold = float(model_test_mingan_copy.name) if model_test_mingan_copy.shape[0] > 0 else 0

    adapt_profit_risk_ratio_ = round(model_test_mingan_copy_['收益风险比'], 4) if model_test_mingan_copy_.shape[0] > 0 else 0
    adapt_winrate_ = round(model_test_mingan_copy_['扣费收益率胜率'], 4) if model_test_mingan_copy_.shape[0] > 0 else 0
    adapt_join_pct_ = round(model_test_mingan_copy_['实际参与率'], 4) if model_test_mingan_copy_.shape[0] > 0 else 0
    adapt_sharpe_ratio_ = round(model_test_mingan_copy_['夏普比率'], 4) if model_test_mingan_copy_.shape[0] > 0 else 0
    adapt_cum_profit_ = round(model_test_mingan_copy_['累计盈利'], 4) if model_test_mingan_copy_.shape[0] > 0 else 0
    adapt_score_threshold_ = in_adapt_score_threshold
    # mean_profit_risk_ratio = round(merge_attend_metric.mean(axis=0).iloc[5], 4)
    # mean_profit_sharp_ratio = round(merge_attend_metric.mean(axis=0).iloc[7], 4)
    watch_scores = {
        '预测值与标签IC': ic,
        '自适应风险收益比': adapt_profit_risk_ratio,
        '自适应扣费收益率胜率': adapt_winrate,
        '自适应参与率': adapt_join_pct,
        '自适应夏普比率': adapt_sharpe_ratio,
        '自适应累计盈利': adapt_cum_profit,
        '自适应阈值': adapt_score_threshold,
        'R自适应风险收益比': adapt_profit_risk_ratio_,
        'R自适应扣费收益率胜率': adapt_winrate_,
        'R自适应参与率': adapt_join_pct_,
        'R自适应夏普比率': adapt_sharpe_ratio_,
        'R自适应累计盈利': adapt_cum_profit_,
        'R自适应阈值': adapt_score_threshold_,
        # '平均收益风险比': mean_profit_risk_ratio,
        # '平均收益夏普比率': mean_profit_sharp_ratio,
    }
    param['score_threshold'] = float(adapt_score_threshold_)

    if fit_cheat_mode:
        pred_result = inst_fit.start_train(param=param)
        inst_fit.hyper_pred_out_path = inst_fit.pred_out_path + f'hyper/{inst_fit.search_time}/'
        FileUtil.save_df2csv(pred_result, inst_fit.hyper_pred_out_path, inst_fit.pred_fname)

        btl_fit.set_valid_fpath(inst_fit.hyper_pred_out_path + inst_fit.pred_fname)
        btl_fit.set_test_fpath(inst_fit.hyper_pred_out_path + inst_fit.pred_fname)
        btl_fit.set_bt_save_path(inst_fit.hyper_pred_out_path)
        model_eval, model_valid_mingan, model_test_mingan = btl_fit.start_backtest()

        model_valid_mingan = model_valid_mingan.sort_values('收益风险比', ascending=False)
        model_valid_mingan['test_indicator'] = model_valid_mingan['收益风险比'] * model_valid_mingan['累计盈利']
        model_valid_mingan_copy = model_valid_mingan.copy()
        model_valid_mingan_copy['fit_indicator'] = model_valid_mingan_copy['收益风险比'] * model_valid_mingan_copy['扣费收益率胜率'] * model_valid_mingan_copy['实际参与率']
        model_valid_mingan_copy = model_valid_mingan_copy.query('0.2 < 实际参与率 < 0.4')  # 控制参与率在0.1-0.3之间
        model_valid_mingan_copy = model_valid_mingan_copy.sort_values(['fit_indicator'], ascending=False).iloc[0]
        in_adapt_score_threshold = model_valid_mingan_copy.name
        model_test_mingan_copy_ = model_test_mingan.loc[in_adapt_score_threshold]

        model_test_mingan = model_test_mingan.sort_values('收益风险比', ascending=False)
        model_test_mingan_copy = model_test_mingan.copy()
        model_test_mingan_copy['fit_indicator'] = model_test_mingan_copy['收益风险比'] * model_test_mingan_copy['扣费收益率胜率'] * model_test_mingan_copy['实际参与率']
        model_test_mingan_copy = model_test_mingan_copy.query('0.2 < 实际参与率 < 0.4')  # 控制参与率在0.1-0.3之间
        model_test_mingan_copy = model_test_mingan_copy.sort_values(['fit_indicator'], ascending=False).iloc[0]

        _ic = round(model_eval['预测值与标签RankIC'], 4) if model_eval.shape[0] > 0 else 0
        _adapt_profit_risk_ratio = round(model_test_mingan_copy['收益风险比'], 4) if model_test_mingan_copy.shape[0] > 0 else 0
        _adapt_winrate = round(model_test_mingan_copy['扣费收益率胜率'], 4) if model_test_mingan_copy.shape[0] > 0 else 0
        _adapt_join_pct = round(model_test_mingan_copy['实际参与率'], 4) if model_test_mingan_copy.shape[0] > 0 else 0
        _adapt_sharpe_ratio = round(model_test_mingan_copy['夏普比率'], 4) if model_test_mingan_copy.shape[0] > 0 else 0
        _adapt_cum_profit = round(model_test_mingan_copy['累计盈利'], 4) if model_test_mingan_copy.shape[0] > 0 else 0
        _adapt_score_threshold = float(model_test_mingan_copy.name) if model_test_mingan_copy.shape[0] > 0 else 0
        # 根据样本内选出的阈值进行计算
        _adapt_profit_risk_ratio_ = round(model_test_mingan_copy_['收益风险比'], 4) if model_test_mingan_copy_.shape[0] > 0 else 0
        _adapt_winrate_ = round(model_test_mingan_copy_['扣费收益率胜率'], 4) if model_test_mingan_copy_.shape[0] > 0 else 0
        _adapt_join_pct_ = round(model_test_mingan_copy_['实际参与率'], 4) if model_test_mingan_copy_.shape[0] > 0 else 0
        _adapt_sharpe_ratio_ = round(model_test_mingan_copy_['夏普比率'], 4) if model_test_mingan_copy_.shape[0] > 0 else 0
        _adapt_cum_profit_ = round(model_test_mingan_copy_['累计盈利'], 4) if model_test_mingan_copy_.shape[0] > 0 else 0
        _adapt_score_threshold_ = in_adapt_score_threshold
        # _mean_profit_risk_ratio = round(merge_attend_metric.mean(axis=0).iloc[5], 4)
        # _mean_profit_sharp_ratio = round(merge_attend_metric.mean(axis=0).iloc[7], 4)

        watch_scores.update({
            '预测值与标签IC2': _ic,
            '自适应风险收益比2': _adapt_profit_risk_ratio,
            '自适应扣费收益率胜率2': _adapt_winrate,
            '自适应参与率2': _adapt_join_pct,
            '自适应夏普比率2': _adapt_sharpe_ratio,
            '自适应累计盈利2': _adapt_cum_profit,
            '自适应阈值2': _adapt_score_threshold,
            'R自适应风险收益比2': _adapt_profit_risk_ratio_,
            'R自适应扣费收益率胜率2': _adapt_winrate_,
            'R自适应参与率2': _adapt_join_pct_,
            'R自适应夏普比率2': _adapt_sharpe_ratio_,
            'R自适应累计盈利2': _adapt_cum_profit_,
            'R自适应阈值2': _adapt_score_threshold_,
            # '平均收益风险比2': _mean_profit_risk_ratio,
            # '平均收益夏普比率2': _mean_profit_sharp_ratio,
        })

    my_logger.info(f'{watch_scores}: {param}')
    inst_test.search_time += 1
    inst_fit.search_time += 1

    return -ic

if hyper_search_mode:
    from hyperopt import fmin, Trials, tpe
    max_evals = 100
    trials = Trials()
    best_param = fmin(tuning_params,
                      space=hyper_params,
                      algo=tpe.suggest,
                      trials=trials,
                      max_evals=max_evals,
                      verbose=True,
                      rstate=np.random.RandomState(2023))
    my_logger.info(f'超参数寻优结束，最优超参数为{best_param}')
else:
    pred_result = inst_test.start_train(param=param_test)
    FileUtil.save_df2csv(pred_result, inst_test.pred_out_path, inst_test.pred_fname)

    # pred_result2 = inst_fit.start_train(param=param_fit)
    # FileUtil.save_df2csv(pred_result2, inst_fit.pred_out_path, inst_fit.pred_fname)
    # check = pred_result2.query('datelist >= "20220101" & prediction == True')

    # inst_fit.date_dict = dict(train_start_date=20160101, train_end_date=20211231, valid_start_date=20210701, valid_end_date=20211231, test_start_date=20211101, test_end_date=20211231)
    # inst_fit.pred_fname = 'prod_for_search_threshold.csv'
    # pred_result = inst_fit.start_train(param=param_fit)
    import json
    inst_fit = inst_test

    inst_fit.model.save_model(junk_path + 'period5_XgbRegModel.pkl')
    with open(junk_path + '_factorName.json', 'w') as f:
        json.dump(inst_fit.factor_list, f, ensure_ascii=False, indent=2)

    factor_scaler_info = pd.DataFrame()
    factor_scaler_info['factorName'] = inst_fit.factor_list
    factor_scaler_info['mean'] = list(inst_fit.scaler.mean_)
    factor_scaler_info['std'] = list(inst_fit.scaler.scale_)
    factor_scaler_info.to_json(junk_path + '_factorScaler.json', orient='records', lines=False, double_precision=15)
    factor_scaler_info['factorName'].to_json(junk_path + '_factorName.json', orient='values')
    with open(junk_path + '_score_threshold.json', 'w') as f:
        json.dump([param_fit['score_threshold']], f, ensure_ascii=False, indent=2)

    # FileUtil.save_df2csv(pred_result, inst_fit.pred_out_path, inst_fit.pred_fname)