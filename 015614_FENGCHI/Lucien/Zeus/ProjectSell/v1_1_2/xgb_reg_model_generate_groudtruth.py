# coding: utf-8
# Author：fengchi863
# Date ：2023/4/25 19:29

# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 8:47
import sys
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import numpy as np
from Zeus.ProjectSell.v1_1_2.path_conf import *
from Zeus.ProjectSell.v1_1_2.hyper_param_space import hyper_xgb_reg_params
import xgboost as xgb
import lightgbm as lgb
import matplotlib
matplotlib.use('Agg')
from sklearn.metrics import roc_curve, auc
from LucienUtil.FileUtil import FileUtil
import matplotlib.pyplot as plt
from Zeus.ProjectSell.v1_1_2.my_logger import MyLogger
from Zeus.BTLite.BTLite2 import BTLite2
import warnings
import os
import json
import joblib
import time
import sys
np.random.seed(2008)
warnings.filterwarnings("ignore")
#
# PERIOD = 'period1'
# SUB_VERSION = f'v{PERIOD[-1]}'
# fs_version = 'rffs' # fsv8, fsv10, fsv11

# 从外部获取
PERIOD = sys.argv[1]
fs_version = sys.argv[2]
SUB_VERSION = f'v{PERIOD[-1]}'
print(PERIOD, fs_version)

hyper_search_mode = False

hyper_params = hyper_xgb_reg_params

class XgbRegModel:
    def __init__(self, sub_version='v1'):
        self.model_name = f'{fs_version}_GroundTruthModel'
        self.strategy_name = 'ProjectSell'
        self.version = 'v1_1_2'
        self.sub_version = sub_version
        self.prefix_path = f'{self.strategy_name}/{self.version}/{self.model_name}/'

        self.pred_out_path = pred_out_path + self.prefix_path
        self.bt_out_path = bt_out_path + self.prefix_path
        self.factor_path = factor_path + self.prefix_path
        self.log_path = log_path + self.prefix_path
        self.eval_path = pred_out_path + self.prefix_path + 'eval/'
        self.hyper_pred_out_path = None
        self.create_floders()

        # 设置参数和阈值
        self.param = {}
        self.best_threshold = 0
        # TODO：如果没有寻优参数文件，那就填写万能参数
        if not hyper_search_mode:
            if PERIOD[-1] == '1':
                self.param = "{'alpha': 0.6, 'booster': 'gbtree', 'colsample_bytree': 0.6, 'eta': 0.005, 'eval_metric': 'rmse', 'evals_result': ('auc', 'rmse'), 'gamma': 0, 'lambda': 0.2, 'max_depth': 8.0, 'min_child_weight': 6.0, 'n_jobs': -1, 'num_boost_round': 1600.0, 'objective': 'reg:linear', 'random_state': 2022, 'scale_pos_weight': 1.0, 'silent': True, 'subsample': 0.9, 'tree_method': 'gpu_hist'}"
                self.best_threshold = 0
            elif PERIOD[-1] == '2':
                self.param = "{'alpha': 0.6, 'booster': 'gbtree', 'colsample_bytree': 0.6, 'eta': 0.005, 'eval_metric': 'rmse', 'evals_result': ('auc', 'rmse'), 'gamma': 0, 'lambda': 0.2, 'max_depth': 8.0, 'min_child_weight': 6.0, 'n_jobs': -1, 'num_boost_round': 1600.0, 'objective': 'reg:linear', 'random_state': 2022, 'scale_pos_weight': 1.0, 'silent': True, 'subsample': 0.9, 'tree_method': 'gpu_hist'}"
                self.best_threshold = 0
            elif PERIOD[-1] == '3':
                self.param = "{'alpha': 0.6, 'booster': 'gbtree', 'colsample_bytree': 0.6, 'eta': 0.005, 'eval_metric': 'rmse', 'evals_result': ('auc', 'rmse'), 'gamma': 0, 'lambda': 0.2, 'max_depth': 8.0, 'min_child_weight': 6.0, 'n_jobs': -1, 'num_boost_round': 1600.0, 'objective': 'reg:linear', 'random_state': 2022, 'scale_pos_weight': 1.0, 'silent': True, 'subsample': 0.9, 'tree_method': 'gpu_hist'}"
                self.best_threshold = 0
            elif PERIOD[-1] == '4':
                self.param = pd.read_excel(self.log_path + f'{self.strategy_name}_{self.version}_{self.model_name}_{self.sub_version}_.xlsx', index_col=0).iloc[0]['整体参数']
                self.best_threshold = 0
            elif PERIOD[-1] == '5':
                self.param = pd.read_excel(self.log_path + f'{self.strategy_name}_{self.version}_{self.model_name}_{self.sub_version}_.xlsx', index_col=0).iloc[0]['整体参数']
                self.best_threshold = 0
            elif PERIOD[-1] == '6':
                self.param = pd.read_excel(self.log_path + f'{self.strategy_name}_{self.version}_{self.model_name}_{self.sub_version}_.xlsx', index_col=0).iloc[0]['整体参数']
                self.best_threshold = 0
            print('最优参数: ', self.param)
            self.param = eval(self.param)

        self.X, self.y = None, None
        self.model = None
        self.scaler = None
        self.label = 'label_diff_pct'
        self.factor_list = None
        self.search_time = 0
        self.date_dict = date_config[f'{PERIOD}']
        self.train_months = None
        self.X_train, self.X_test, self.X_fit, self.y_train, self.y_test, self.y_fit= None, None, None, None, None, None
        self.y_test_pred, self.y_fit_pred = None, None
        self.test_pred_fname = f'{self.date_dict["test_start_date"]}~{self.date_dict["test_end_date"]}_{self.model_name}_{self.sub_version}.csv'
        self.fit_pred_fname = f'{self.date_dict["fit_start_date"]}~{self.date_dict["fit_end_date"]}_{self.model_name}_{self.sub_version}.csv'

        self.get_dataset(data_test_fpath_with_label)

    def create_floders(self):
        os.makedirs(self.pred_out_path, exist_ok=True)
        os.makedirs(self.bt_out_path, exist_ok=True)
        os.makedirs(self.factor_path, exist_ok=True)
        os.makedirs(self.log_path, exist_ok=True)
        os.makedirs(self.eval_path, exist_ok=True)

    def get_dataset(self, path):
        samples = pd.read_pickle(path)
        X = samples[filter(lambda x: x.find('label'), samples.columns.tolist())]
        X = X.dropna(how='any', axis=0)
        X = samples.loc[X.index]

        # y = pd.read_hdf(profit_data_fpath)
        y = samples[[self.label]]

        y.columns = [self.label]

        y = y.reindex(index=X.index)

        y = y.drop(np.isnan(y)[self.label][np.isnan(y)[self.label]].index)
        X = X.reindex(index=y.index)

        self.X = X
        self.y = y

    def filter_factor(self, xgb_imptc_fpath=None, factor_score_fpath=factor_score_fpath):
        # TODO：使用哪种因子版本，统一的版本还是自己开发的版本
        if fs_version == 'rffs':
            factor_list = pd.read_pickle(f'/data/user/015614/Zeus/factor_select/ProjectSell/v1_1_2/rffs_{PERIOD}.pkl')
        elif fs_version == 'fsrs':
            factor_list = pd.read_excel(eval(f'fsrs_imptc_{PERIOD}_fpath'), index_col=0)
            factor_list = factor_list.query('select == 1').index.tolist()
        else:
            factor_list = self.fun_filter_factor(xgb_imptc_fpath=xgb_imptc_fpath, factor_score_fpath=factor_score_fpath)
        print(f'use {len(factor_list)} factors')
        self.factor_list = factor_list
        return factor_list

    @staticmethod
    def fun_filter_factor(xgb_imptc_fpath=None, factor_score_fpath=None):
        filter_factor_df = pd.read_excel(xgb_imptc_fpath, index_col=0)
        _xgb_imptc_factor = filter_factor_df.query('corr_selected==1')
        factor_list = _xgb_imptc_factor['factor_name'].tolist()
        return factor_list

    # 使用month进行tscv
    def get_tscv(self, rolling_size=7, valid_size=4, min_train_size=18):
        month_list = self.train_months
        rolling_cv_month_list = list()
        train_start_idx = 0
        train_end_idx = min_train_size - 1
        valid_start_idx = train_end_idx + 1
        valid_end_idx = train_end_idx + valid_size
        while valid_end_idx < len(month_list):
            tmp_cv = list(map(lambda x: month_list[x], [train_start_idx, train_end_idx, valid_start_idx, valid_end_idx]))
            rolling_cv_month_list.append(tmp_cv)
            train_end_idx += rolling_size
            valid_start_idx = train_end_idx + 1
            valid_end_idx = train_end_idx + valid_size
        if rolling_cv_month_list[-1][-1] > month_list[-1]:
            valid_end_idx = len(month_list) - 1
            valid_start_idx = len(month_list) - valid_size
            train_end_idx = valid_start_idx - 1
            tmp_cv = list(map(lambda x: month_list[x], [train_start_idx, train_end_idx, valid_start_idx, valid_end_idx]))
            rolling_cv_month_list.append(tmp_cv)
        return rolling_cv_month_list

    def get_train_and_test_data(self):
        X_copy = self.X.copy()
        y_copy = self.y.copy()
        X_copy = X_copy.drop(X_copy.filter(regex='label*').columns.tolist(), axis=1)
        y_copy = y_copy.reindex(index=X_copy.index)

        if fs_version in ['fsv8', 'fsv10', 'fsv11']:
            filtered_factor = self.filter_factor(xgb_imptc_fpath=eval(f'xgb_imptc_{fs_version}_{PERIOD}_fpath'))
        else:
            filtered_factor = self.filter_factor(xgb_imptc_fpath=eval(f'xgb_imptc_fsv8_{PERIOD}_fpath'))

        X_copy = X_copy[filtered_factor]

        X_copy['trade_date'] = X_copy.index.get_level_values(1).strftime('%Y%m%d').astype(int).tolist()
        y_copy['trade_date'] = y_copy.index.get_level_values(1).strftime('%Y%m%d').astype(int).tolist()

        X_train = X_copy.query(f'trade_date >= {self.date_dict["train_start_date"]} & trade_date <= {self.date_dict["valid_end_date"]}')
        y_train = y_copy.query(f'trade_date >= {self.date_dict["train_start_date"]} & trade_date <= {self.date_dict["valid_end_date"]}')
        X_test = X_copy.query(f'trade_date >= {self.date_dict["test_start_date"]} & trade_date <= {self.date_dict["test_end_date"]}')
        y_test = y_copy.query(f'trade_date >= {self.date_dict["test_start_date"]} & trade_date <= {self.date_dict["test_end_date"]}')
        X_fit = X_copy.query(f'trade_date >= {self.date_dict["fit_start_date"]} & trade_date <= {self.date_dict["fit_end_date"]}')
        y_fit = y_copy.query(f'trade_date >= {self.date_dict["fit_start_date"]} & trade_date <= {self.date_dict["fit_end_date"]}')

        y_train = y_train[[self.label]]
        y_test = y_test[[self.label]]
        y_fit = y_fit[[self.label]]

        self.train_months = list(sorted(set((X_train['trade_date'] // 100).tolist())))

        X_train = X_train.drop('trade_date', axis=1)
        X_test = X_test.drop('trade_date', axis=1)
        X_fit = X_fit.drop('trade_date', axis=1)

        self.X_train, self.X_test, self.X_fit, self.y_train, self.y_test, self.y_fit = X_train, X_test, X_fit, y_train, y_test, y_fit

    @staticmethod
    def func_trans_train_test_with_scaler(_arr, scaler):
        n, median, mad, data_min, data_max = scaler
        arr = _arr.copy()
        arr1 = np.where(arr > (median + n * mad), np.repeat((median + n * mad)[None, :], arr.shape[0], 0), arr)
        arr2 = np.where(arr1 < (median - n * mad), np.repeat((median - n * mad)[None, :], arr1.shape[0], 0), arr1)
        arr_sclaled = (arr2 - data_min) / (data_max - data_min)
        return arr_sclaled

    def func_trans_train_test_minmaxmadscaler(self, X_train, X_test):
        train_data = X_train

        def _func_median_mad(_arr, n):
            arr = _arr.copy()
            median = np.median(arr, axis=0)
            mad = np.median(np.abs(arr - median), axis=0)
            arr1 = np.where(arr > (median + n * mad), np.repeat((median + n * mad)[None, :], arr.shape[0], 0), arr)
            arr2 = np.where(arr1 < (median - n * mad), np.repeat((median - n * mad)[None, :], arr1.shape[0], 0), arr1)
            return arr2, median, mad

        def _fit_minmax_median_mad(_arr, n=3):
            arr = _arr.copy()
            arr2, median, mad = _func_median_mad(arr, n)
            data_min = np.min(arr2, axis=0)
            data_max = np.max(arr2, axis=0)
            data_max = np.where(data_min == data_max, 1, data_max)  # 防止出现为nan的情况
            return n, median, mad, data_min, data_max

        n, median, mad, train_min, train_max = _fit_minmax_median_mad(train_data.values, n=5)
        self.scaler = (n, median, mad, train_min, train_max)
        X_train_scaled_array = self.func_trans_train_test_with_scaler(X_train.values, self.scaler)
        X_test_scaled_array = self.func_trans_train_test_with_scaler(X_test.values, self.scaler)

        X_train_scaled = pd.DataFrame(X_train_scaled_array, index=X_train.index, columns=X_train.columns)
        X_test_scaled = pd.DataFrame(X_test_scaled_array, index=X_test.index, columns=X_test.columns)

        return X_train_scaled, X_test_scaled

    def train_model(self, X_train, y_train, param, X_valid=None, y_valid=None, stage='no_draw'):
        dtrain = xgb.DMatrix(X_train, y_train)
        dvalid = xgb.DMatrix(X_valid, y_valid)
        eval_result = {}

        num_boost_round = int(param.pop('num_boost_round'))
        model = xgb.train(param, dtrain,
                          num_boost_round=num_boost_round,
                          evals=[(dtrain, 'train'), (dvalid, 'valid')],
                          evals_result=eval_result,
                          verbose_eval=0)

        if not hyper_search_mode and stage is 'draw':
            # 绘制早停测试图形
            import matplotlib.pyplot as plt
            lgb.plot_metric(eval_result, metric='rmse')
            plt.savefig(self.eval_path + f'auc_{PERIOD}.png', bbox_inches='tight', pad_inches=0.0)
            # lgb.plot_metric(eval_result, metric='auc')
            # plt.savefig(self.eval_path + f'logloss_{PERIOD}.png', bbox_inches='tight', pad_inches=0.0)

        self.model = model

    def predict(self, X_other):
        _y_pred = self.model.predict(X_other)
        return _y_pred

    def model_eval(self, y_true, y_pred, score_threshold=0.0, stage='test'):
        y_true_label = y_true.values.reshape(-1) > 0
        y_pred_label = y_pred > score_threshold
        fpr, tpr, th = roc_curve(y_true_label, y_pred, pos_label=1)

        # 绘制ROC曲线，可以尝试根据fpr序列中间那个数的值进行参与率的选取
        if not hyper_search_mode and stage != 'no_draw':
            import matplotlib.pyplot as plt
            plt.figure(figsize=(15, 15))
            plt.plot(fpr, tpr, lw=5, label='')
            plt.plot([0, 1], [0, 1], '--', lw=5, color='grey', label=f'AUC={round(auc(fpr, tpr), 3)}')
            plt.axis('square')
            plt.xlim([0, 1])
            plt.ylim([0, 1])
            plt.xlabel('False Positive Rate', fontsize=20)
            plt.ylabel('True Positive Rate', fontsize=20)
            plt.title('ROC Curve', fontsize=25)
            plt.legend(loc='lower right', fontsize=20)
            plt.savefig(self.eval_path + f'roc_curve_{PERIOD}_{stage}.png', bbox_inches='tight', pad_inches=0.0)

        eval_auc = auc(fpr, tpr)
        eval_precision = float(np.mean(y_true_label[y_pred_label == 1]))
        eval_recall = float(np.mean(y_pred_label[y_true_label == 1]))
        eval_rmse = ((y_true.values[:, 0] - y_pred) ** 2).mean() ** 0.5
        eval_ic = pd.DataFrame([y_true.values.reshape(-1), y_pred]).T.corr('spearman').iloc[0, 1]
        return eval_auc, eval_precision, eval_recall, eval_rmse, eval_ic, y_pred_label

    def tscv_eval_model(self, param):
        rolling_cv_month_list = self.get_tscv()
        eval_auc_list, eval_precision_list, eval_recall_list, eval_rmse_list, eval_ic_list = list(), list(), list(), list(), list()
        for idx, cv_list in enumerate(rolling_cv_month_list):
            if not hyper_search_mode:
                continue
            train_start_month, train_end_month, valid_start_month, valid_end_month = cv_list[0], cv_list[1], cv_list[2], cv_list[3]
            X_train_all = self.X_train.copy()
            y_train_all = self.y_train.copy()
            X_train_all['trade_month'] = X_train_all.index.get_level_values(1).strftime('%Y%m').astype(int)
            y_train_all['trade_month'] = y_train_all.index.get_level_values(1).strftime('%Y%m').astype(int)
            X_train = X_train_all.query(f'trade_month >= {train_start_month} & trade_month <= {train_end_month}').drop('trade_month', axis=1)
            X_valid = X_train_all.query(f'trade_month >= {valid_start_month} & trade_month <= {valid_end_month}').drop('trade_month', axis=1)
            y_train = y_train_all.query(f'trade_month >= {train_start_month} & trade_month <= {train_end_month}').drop('trade_month', axis=1)
            y_valid = y_train_all.query(f'trade_month >= {valid_start_month} & trade_month <= {valid_end_month}').drop('trade_month', axis=1)
            X_train_scaled, X_test_scaled = self.func_trans_train_test_minmaxmadscaler(X_train, X_valid)

            self.train_model(X_train_scaled, y_train, param.copy(), X_valid=X_test_scaled, y_valid=y_valid, stage='no_draw')
            dtest = xgb.DMatrix(X_test_scaled)
            y_valid_pred = self.predict(dtest)

            eval_auc, eval_precision, eval_recall, eval_rmse, eval_ic, y_pred_label = self.model_eval(y_valid, y_valid_pred, score_threshold=self.best_threshold, stage='no_draw')
            print(f'第{idx + 1}折结果：{round(eval_auc, 4)}, {round(eval_precision, 4)}, {round(eval_recall, 4)}, {round(eval_rmse, 4)}, {round(eval_ic, 4)}')
            eval_auc_list.append(eval_auc)
            eval_precision_list.append(eval_precision)
            eval_recall_list.append(eval_recall)
            eval_rmse_list.append(eval_rmse)
            eval_ic_list.append(eval_ic)

        eval_auc_mean = np.mean(eval_auc_list)
        eval_auc_std = np.std(eval_auc_list)
        eval_precision_mean = np.mean(eval_precision_list)
        eval_recall_mean = np.mean(eval_recall_list)
        eval_rmse_mean = np.mean(eval_rmse_list)
        eval_ic_mean = np.mean(eval_ic_list)
        print(f'该参数下表现均值为：{round(eval_auc_mean, 4)}, {round(eval_auc_std, 4)}, {round(eval_precision_mean, 4)}, '
              f'{round(eval_recall_mean, 4)}, {round(eval_rmse_mean, 4)}, {round(eval_ic_mean, 4)}')
        return eval_auc_mean, eval_auc_std, eval_precision_mean, eval_recall_mean, eval_rmse_mean, eval_ic_mean

    @staticmethod
    def tranfrom_pred_data(y_test_pred, index, score_threshold=0.0):
        test_pred = list(y_test_pred > score_threshold)
        test_pred_prob = list(y_test_pred)
        test_pred_df = pd.DataFrame(index=index)
        test_pred_df['prediction'] = test_pred
        test_pred_df['pred_Reg'] = test_pred_prob
        test_pred_df['stockID'] = test_pred_df.index.get_level_values(2)
        test_pred_df['datelist'] = test_pred_df.index.get_level_values(1).strftime('%Y%m%d')
        test_pred_df['s_xx'] = test_pred_df.index.get_level_values(0).map(str)
        test_pred_df['Indexs'] = test_pred_df['stockID'] + ' ' + test_pred_df['datelist'] + ' ' + test_pred_df['s_xx']
        test_pred_df = test_pred_df.set_index('Indexs', drop=True)
        return test_pred_df

    def start_train(self, param):
        param_copy = param.copy()
        if 'n_estimators' in param_copy.keys():
            param_copy['n_estimators'] = int(param_copy['n_estimators'])
        if 'factor_num' in param_copy.keys():
            param_copy['factor_num'] = int(param_copy['factor_num'])
        if 'max_depth' in param_copy.keys():
            param_copy['max_depth'] = int(param_copy['max_depth'])
        if 'num_leaves' in param_copy.keys():
            param_copy['num_leaves'] = int(param_copy['num_leaves'])
        if 'min_data_in_leaf' in param_copy.keys():
            param_copy['min_data_in_leaf'] = int(param_copy['min_data_in_leaf'])
        if 'min_child_samples' in param_copy.keys():
            param_copy['min_child_samples'] = int(param_copy['min_child_samples'])

        self.get_train_and_test_data()
        valid_auc, valid_auc_std, valid_precision, valid_recall, valid_rmse, valid_ic = self.tscv_eval_model(param=param_copy)

        X_train_scaled, X_test_scaled = self.func_trans_train_test_minmaxmadscaler(self.X_train, self.X_test)
        self.train_model(X_train_scaled, self.y_train, param_copy, X_test_scaled, self.y_test, stage='draw')

        dtest = xgb.DMatrix(X_test_scaled)
        y_test_pred = self.y_test.values[:, 0] # self.predict(dtest)
        test_auc, test_precision, test_recall, test_rmse, test_ic, y_test_pred_label = self.model_eval(self.y_test, y_test_pred, score_threshold=self.best_threshold, stage='test')
        print(f'test区间结果：{round(test_auc, 4)}, {round(test_precision, 4)}, {round(test_recall, 4)}, {round(test_rmse, 4)}')
        self.y_test_pred = y_test_pred

        X_fit_scaled = self.func_trans_train_test_with_scaler(self.X_fit, self.scaler)
        X_fit_scaled = pd.DataFrame(X_fit_scaled, index=self.X_fit.index, columns=self.X_fit.columns)
        dfit = xgb.DMatrix(X_fit_scaled)
        y_fit_pred = self.y_fit.values[:, 0] # self.predict(dfit)
        fit_auc, fit_precision, fit_recall, fit_rmse, fit_ic, y_fit_pred_label = self.model_eval(self.y_fit, y_fit_pred, score_threshold=self.best_threshold, stage='fit')
        print(f'fit区间结果：{round(fit_auc, 4)}, {round(fit_precision, 4)}, {round(fit_recall, 4)}, {round(fit_rmse, 4)}')
        self.y_fit_pred = y_fit_pred

        return valid_auc, ((valid_auc, valid_auc_std, valid_precision, valid_recall, valid_rmse, valid_ic),
                           (test_auc, test_precision, test_recall, test_rmse, test_ic),
                           (fit_auc, fit_precision, fit_recall, fit_rmse, fit_ic))

inst = XgbRegModel(sub_version=SUB_VERSION)

if hyper_search_mode:
    my_logger = MyLogger(strategy_name=inst.strategy_name, model_name=inst.model_name, version=inst.version, sub_version=inst.sub_version).get_logger()
    my_logger.info(f'{inst.strategy_name} {inst.version} {inst.model_name} {inst.sub_version}')
else:
    my_logger = None

# btl = BTLite2(strategy_name='ProjectSell',
#               model_name='SingleTestModel',
#               date_dict=date_config[f'{PERIOD}'],
#               bt_save_path=junk_path + '回测结果/',
#               test_fpath=None,
#               fit_fpath=None)

def tuning_params(param):
    param['colsample_bytree'] = round(param['colsample_bytree'], 1)
    param['alpha'] = round(param['alpha'], 1)
    param['lambda'] = round(param['lambda'], 1)
    param['subsample'] = round(param['subsample'], 1)

    valid_auc, eval_tuple = inst.start_train(param)
    inst.hyper_pred_out_path = inst.pred_out_path + f'hyper/{inst.search_time}/'

    y_test_pred_df = inst.tranfrom_pred_data(inst.y_test_pred, index=inst.y_test.index, score_threshold=inst.best_threshold)
    FileUtil.save_df2csv(y_test_pred_df, inst.hyper_pred_out_path, inst.test_pred_fname)

    y_fit_pred_df = inst.tranfrom_pred_data(inst.y_fit_pred, index=inst.y_fit.index, score_threshold=inst.best_threshold)
    FileUtil.save_df2csv(y_fit_pred_df, inst.hyper_pred_out_path, inst.fit_pred_fname)

    # btl.set_test_fpath(inst.hyper_pred_out_path + inst.test_pred_fname)
    # btl.set_fit_fpath(inst.hyper_pred_out_path + inst.fit_pred_fname)
    # btl.set_bt_save_path(inst.hyper_pred_out_path)
    # model_eval, model_test_mingan, model_fit_mingan = btl.start_backtest()
    # eval_output_dict = {'模型评估': model_eval,
    #                     'test区间不同参与率': model_test_mingan,
    #                     'fit区间不同参与率': model_fit_mingan}
    # FileUtil.save_dict2xls(eval_output_dict, inst.hyper_pred_out_path, '回测结果.xlsx')

    watch_scores = {
        'valid_auc': eval_tuple[0][0],
        'valid_auc_std': eval_tuple[0][1],
        'valid_precision': eval_tuple[0][2],
        'valid_recall': eval_tuple[0][3],
        'valid_rmse': eval_tuple[0][4],
        'valid_ic': eval_tuple[0][5],
        'test_auc': eval_tuple[1][0],
        'test_precision': eval_tuple[1][1],
        'test_recall': eval_tuple[1][2],
        'test_rmse': eval_tuple[1][3],
        'test_ic': eval_tuple[1][4],
        'fit_auc': eval_tuple[2][0],
        'fit_precision': eval_tuple[2][1],
        'fit_recall': eval_tuple[2][2],
        'fit_rmse': eval_tuple[2][3],
        'fit_ic': eval_tuple[2][4],
        # 'test_收益夏普比率': model_test_mingan['收益夏普比率'].mean(),
        # 'test_收益风险比': model_test_mingan['收益风险比'].mean(),
        # 'fit_收益夏普比率': model_fit_mingan['收益夏普比率'].mean(),
        # 'fit_收益风险比': model_fit_mingan['收益风险比'].mean(),
    }

    my_logger.info(f'{watch_scores}: {param}')
    inst.search_time += 1

    return -valid_auc


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
    valid_auc, eval_tuple = inst.start_train(inst.param)

    y_test_pred_df = inst.tranfrom_pred_data(inst.y_test_pred, index=inst.y_test.index, score_threshold=inst.best_threshold)
    FileUtil.save_df2csv(y_test_pred_df, inst.pred_out_path, inst.test_pred_fname)

    y_fit_pred_df = inst.tranfrom_pred_data(inst.y_fit_pred, index=inst.y_fit.index, score_threshold=inst.best_threshold)
    FileUtil.save_df2csv(y_fit_pred_df, inst.pred_out_path, inst.fit_pred_fname)
    # 保存模型
    os.makedirs(junk_path + f'{inst.model_name}/', exist_ok=True)
    junk_path = junk_path + f'{inst.model_name}/'
    inst.model.save_model(junk_path + 'XgbRegModel.pkl')
    with open(junk_path + '_factorName.json', 'w') as f:
        json.dump(inst.factor_list, f, ensure_ascii=False, indent=2)

    factor_scaler_info = pd.DataFrame()
    factor_scaler_info['factorName'] = inst.factor_list
    factor_scaler_info['n'] = inst.scaler[0]
    factor_scaler_info['median'] = list(inst.scaler[1])
    factor_scaler_info['mad'] = list(inst.scaler[2])
    factor_scaler_info['train_min'] = list(inst.scaler[3])
    factor_scaler_info['train_max'] = list(inst.scaler[4])
    factor_scaler_info.to_json(junk_path + '_factorScaler.json', orient='records', lines=False, double_precision=15)
    factor_scaler_info['factorName'].to_json(junk_path + '_factorName.json', orient='values')
    with open(junk_path + '_score_threshold.json', 'w') as f:
        json.dump([inst.best_threshold], f, ensure_ascii=False, indent=2)