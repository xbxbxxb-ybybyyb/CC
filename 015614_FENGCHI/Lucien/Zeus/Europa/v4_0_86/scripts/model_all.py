# coding: utf-8
# Author：fengchi863
# Date ：2023/8/16 10:29

import sys
sys.path.append('/data/user/015614/Lucien')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# from Zeus.Europa.v4_0_86.backtest.SimBackTest import SimBackTest

import pandas as pd
import numpy as np
from tqdm import tqdm
from joblib import Parallel, delayed
import importlib
from Zeus.Europa.v4_0_86.backtest.SimBackTest import SimBackTest
from Zeus.Europa.v4_0_86.config.strat_conf import *
from Zeus.Europa.v4_0_86.scripts.hyper_param_space import *
from Zeus.Europa.v4_0_86.label_generate.fetch_label import fetch_label
import xgboost as xgb
import lightgbm as lgb
from Zeus.Europa.v4_0_86.models.MlpRegModel import MlpRegModel
from sklearn.metrics import roc_curve, auc
from LucienUtil.FileUtil import FileUtil
from Zeus.Europa.v4_0_86.scripts.my_logger import MyLogger
import warnings
import random
import os
gpu_id = random.randint(0, 2)
# gpu_id = 0
os.environ['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
import json
import joblib
import time
import sys
warnings.filterwarnings("ignore")

gamma = 2
alpha = 0.3
def loss_fun1(p, dtrain):
    y = dtrain.get_label()
    p = 1.0 / (1.0 + np.exp(-p))
    grad = p * (1 - p) * (alpha * gamma * y * (1 - p) ** gamma * np.log(p) / (1 - p) - alpha * y * (
                1 - p) ** gamma / p - gamma * p ** gamma * (1 - alpha) * (1 - y) * np.log(1 - p) / p + p ** gamma * (
                                      1 - alpha) * (1 - y) / (1 - p))
    hess = p * (1 - p) * (p * (1 - p) * (
                -alpha * gamma ** 2 * y * (1 - p) ** gamma * np.log(p) / (1 - p) ** 2 + alpha * gamma * y * (
                    1 - p) ** gamma * np.log(p) / (1 - p) ** 2 + 2 * alpha * gamma * y * (1 - p) ** gamma / (
                            p * (1 - p)) + alpha * y * (1 - p) ** gamma / p ** 2 - gamma ** 2 * p ** gamma * (
                            1 - alpha) * (1 - y) * np.log(1 - p) / p ** 2 + 2 * gamma * p ** gamma * (1 - alpha) * (
                            1 - y) / (p * (1 - p)) + gamma * p ** gamma * (1 - alpha) * (1 - y) * np.log(
                            1 - p) / p ** 2 + p ** gamma * (1 - alpha) * (1 - y) / (1 - p) ** 2) - p * (
                                      alpha * gamma * y * (1 - p) ** gamma * np.log(p) / (1 - p) - alpha * y * (
                                          1 - p) ** gamma / p - gamma * p ** gamma * (1 - alpha) * (1 - y) * np.log(
                                  1 - p) / p + p ** gamma * (1 - alpha) * (1 - y) / (1 - p)) + (1 - p) * (
                                      alpha * gamma * y * (1 - p) ** gamma * np.log(p) / (1 - p) - alpha * y * (
                                          1 - p) ** gamma / p - gamma * p ** gamma * (1 - alpha) * (1 - y) * np.log(
                                  1 - p) / p + p ** gamma * (1 - alpha) * (1 - y) / (1 - p)))
    return grad, hess


"""确定选用的区间、因子筛选、标签、模型、是否超参数寻优"""
if len(sys.argv) > 1:
    period = sys.argv[1]
    fs_version = sys.argv[2]
    config_flag = sys.argv[3]
    label_trans = sys.argv[4]
    model_select = sys.argv[5]
    scaler_select = sys.argv[6]
    hyper_search_mode = int(sys.argv[7])
    attend_ratio = int(sys.argv[8])
    seed = int(sys.argv[9])
else:
    period = 'period4'
    fs_version = 'fsv8' # fsv8\fsv10\fsv11\rffs
    config_flag = 'config7'
    label_trans = 'lt1'
    model_select = 'XgbRegModel'
    scaler_select = 'scaler1'
    hyper_search_mode = 2
    attend_ratio = 40
    seed = 0
print(period, fs_version, config_flag, label_trans, model_select, scaler_select, hyper_search_mode, attend_ratio)
module_name = f'Zeus.Europa.v4_0_86.config.path_conf'
module = importlib.import_module(module_name)
PT = getattr(module, config_flag)

label = PT['label']
data_fpath = PT['data_fpath']
profit_data_fpath = PT['profit_data_fpath']
fsv8_fpath = PT[f'xgb_fsv8_{period.replace("_roll", "")}_fpath']
fsv10_fpath = PT[f'xgb_fsv10_{period.replace("_roll", "")}_fpath']
fsv11_fpath = PT[f'xgb_fsv11_{period.replace("_roll", "")}_fpath']
fsrs_fpath = PT[f'fsrs_{period.replace("_roll", "")}_fpath']
fsci_fpath = PT[f'fsci_{period.replace("_roll", "")}_fpath']
fs_config = PT['fs_config']

"""确定选用的参数"""
if model_select == 'XgbRegModel':
    fixed_params = fixed_xgb_reg_param[fs_version]
elif model_select == 'LgbRegModel':
    fixed_params = fixed_lgb_reg_param[fs_version]
    # os.environ['CUDA_LAUNCH_BLOCKING'] = '2'
elif model_select == 'MlpRegModel':
    fixed_params = fixed_mlp_reg_param[fs_version]
    # os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
elif model_select == 'LrRegModel':
    fixed_params = hyper_lr_reg_params
else:
    raise Exception('模型名字输入错误！！！')

# 状态机，当mode==2时，在fix_params的基础上把树的数量增加
if hyper_search_mode == 2:
    tree_num_list = list(range(300, 1500, 100)) + list(range(1500, 3100, 300))
    if model_select == 'XgbRegModel':
        hyper2_xgb_reg_params_list = [add(fixed_params, {'num_boost_round': x}) for x in tree_num_list]
    elif model_select == 'LgbRegModel':
        hyper2_lgb_reg_params_list = [add(fixed_params, {'n_estimators': x}) for x in tree_num_list]

"""
model_name: like fsv8_pct_XgbRegModel...
model: like XgbRegModel...
version: like v1_0_0...
strategy_name: like Europa, Jupiter...
"""
class MyModelTrain:
    def __init__(self, model_select='XgbRegModel'):

        # 为了保证表格sheet_name长度不超过31字符，这里使用简写，以及去除没有区分度的字段
        scaler_select_abbr = scaler_select[0] + scaler_select[-1]
        model_select_abbr = model_select[:3]
        self.model_name = f'{fs_version}_{scaler_select_abbr}_{model_select_abbr}'

        self.model_select = model_select
        self.strategy_name = 'Europa'
        self.version = STRATEGY_VERSION
        self.attend_ratio = attend_ratio
        self.best_threshold = 0
        self.prefix_path = f'{self.strategy_name}/{self.version}/{config_flag}/{self.model_name}/'

        self.pred_out_path = pred_out_path + self.prefix_path
        self.bt_out_path = bt_out_path + self.prefix_path
        self.factor_path = factor_path + self.prefix_path
        self.log_path = log_path + self.prefix_path
        self.eval_path = pred_out_path + self.prefix_path + 'eval/'
        self.hyper_pred_out_path = None
        self.create_floders()

        # 设置参数和阈值
        self.param = {}
        # TODO：如果没有寻优参数文件，那就填写万能参数
        if hyper_search_mode == 0:
            self.param = fixed_params
            if 'seed' in self.param.keys():
                if 0 < seed < 31:
                    self.param['seed'] = seed
                else:
                    pass
            # print('最优参数: ', self.param)
        # print(self.param['seed'])
        self.X, self.y = None, None
        self.model = None
        self.scaler = None
        self.label = PT['label']

        self.factor_list = None
        self.search_time = 0
        self.date_dict = DATE_CONFIG[f'{period}']
        self.train_months = None
        self.X_train, self.X_test, self.X_fit, self.y_train, self.y_test, self.y_fit = None, None, None, None, None, None
        self.y_test_pred, self.y_fit_pred = None, None
        self.test_pred_fname = f'{self.date_dict["test_start_date"]}~{self.date_dict["test_end_date"]}.csv'
        self.fit_pred_fname = f'{self.date_dict["fit_start_date"]}~{self.date_dict["fit_end_date"]}.csv'

        self.get_dataset(data_fpath)

    def create_floders(self):
        os.makedirs(self.pred_out_path, exist_ok=True)
        os.makedirs(self.bt_out_path, exist_ok=True)
        os.makedirs(self.factor_path, exist_ok=True)
        os.makedirs(self.log_path, exist_ok=True)
        # os.makedirs(self.eval_path, exist_ok=True)

    def get_dataset(self, path):
        samples = pd.read_pickle(path)
        X = samples[filter(lambda x: x.find('label'), samples.columns.tolist())]
        X = X.dropna(how='any', axis=0)
        X = samples.loc[X.index]

        # y = pd.read_hdf(profit_data_fpath)
        if 'self' in self.label:
            y = fetch_label(config_flag)
        else:
            y = samples[[self.label]]
            y.columns = [self.label]

        y = y.reindex(index=X.index)
        y = y.drop(np.isnan(y)[self.label][np.isnan(y)[self.label]].index)
        X = X.reindex(index=y.index)

        self.X = X
        self.y = y

    def select_factor(self):
        if fs_version in ['fsv8', 'fsv10', 'fsv11']:
            xgb_imptc_fpath = eval(f'{fs_version}_fpath')
            filter_factor_df = pd.read_excel(xgb_imptc_fpath, index_col=0)
            _xgb_imptc_factor = filter_factor_df.query('corr_selected==1')
            factor_list = _xgb_imptc_factor['factor_name'].tolist()
        elif fs_version in ['fsrs', 'fsci']:
            factor_list = pd.read_excel(eval(f'{fs_version}_fpath')).set_index('factor_name')
            factor_list = factor_list.query('select == 1').index.tolist()
        else:
            try:
                factor_list = pd.read_pickle(eval(fs_config[fs_version]))
            except:
                raise Exception('因子筛选输入错误！！！')
        print(f'{period} {label} | use {fs_version} which includes {len(factor_list)} factors and use No.{gpu_id} GPU')
        self.factor_list = factor_list
        return factor_list

    def get_train_and_test_data(self):
        X_copy = self.X.copy()
        y_copy = self.y.copy()
        X_copy = X_copy.drop(X_copy.filter(regex='label*').columns.tolist(), axis=1)
        y_copy = y_copy.reindex(index=X_copy.index)

        filtered_factor = self.select_factor()
        X_copy = X_copy[filtered_factor]

        X_copy['trade_date'] = X_copy.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
        y_copy['trade_date'] = y_copy.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()

        X_train = X_copy.query(f'trade_date >= {self.date_dict["train_start_date"]} & trade_date <= {self.date_dict["valid_end_date"]}')
        y_train = y_copy.query(f'trade_date >= {self.date_dict["train_start_date"]} & trade_date <= {self.date_dict["valid_end_date"]}')
        X_test = X_copy.query(f'trade_date >= {self.date_dict["test_start_date"]} & trade_date <= {self.date_dict["test_end_date"]}')
        y_test = y_copy.query(f'trade_date >= {self.date_dict["test_start_date"]} & trade_date <= {self.date_dict["test_end_date"]}')
        X_fit = X_copy.query(f'trade_date >= {self.date_dict["fit_start_date"]} & trade_date <= {self.date_dict["fit_end_date"]}')
        y_fit = y_copy.query(f'trade_date >= {self.date_dict["fit_start_date"]} & trade_date <= {self.date_dict["fit_end_date"]}')

        y_train = y_train[[self.label]]
        y_test = y_test[[self.label]]
        y_fit = y_fit[[self.label]]

        X_train = X_train.drop('trade_date', axis=1)
        X_test = X_test.drop('trade_date', axis=1)
        X_fit = X_fit.drop('trade_date', axis=1)

        self.X_train, self.X_test, self.X_fit, self.y_train, self.y_test, self.y_fit = X_train, X_test, X_fit, y_train, y_test, y_fit

    @staticmethod
    def func_trans_train_test_with_scaler1(_arr, scaler):
        n, median, mad, data_min, data_max = scaler
        arr = _arr.copy()
        arr1 = np.where(arr > (median + n * mad), np.repeat((median + n * mad)[None, :], arr.shape[0], 0), arr)
        arr2 = np.where(arr1 < (median - n * mad), np.repeat((median - n * mad)[None, :], arr1.shape[0], 0), arr1)
        arr_sclaled = (arr2 - data_min) / (data_max - data_min)
        return arr_sclaled

    def func_trans_train_test_scaler1(self, X_train, X_test):
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
        X_train_scaled_array = self.func_trans_train_test_with_scaler1(X_train.values, self.scaler)
        X_test_scaled_array = self.func_trans_train_test_with_scaler1(X_test.values, self.scaler)

        X_train_scaled = pd.DataFrame(X_train_scaled_array, index=X_train.index, columns=X_train.columns)
        X_test_scaled = pd.DataFrame(X_test_scaled_array, index=X_test.index, columns=X_test.columns)

        return X_train_scaled, X_test_scaled

    @staticmethod
    def func_trans_train_test_with_scaler2(_arr, scaler):
        arr_std, arr_mean = scaler
        arr = _arr.copy()
        arr_sclaled = (arr - arr_mean) / arr_std
        return arr_sclaled

    def func_trans_train_test_scaler2(self, X_train, X_test):
        arr_ = X_train.values.copy()
        arr_std = np.std(arr_, axis=0)
        arr_mean = np.mean(arr_, axis=0)
        self.scaler = (arr_std, arr_mean)
        X_train_scaled_array = (X_train.values - arr_mean) / arr_std
        X_test_scaled_array = (X_test.values - arr_mean) / arr_std

        X_train_scaled = pd.DataFrame(X_train_scaled_array, index=X_train.index, columns=X_train.columns)
        X_test_scaled = pd.DataFrame(X_test_scaled_array, index=X_test.index, columns=X_test.columns)

        return X_train_scaled, X_test_scaled


    """根据model名字选择实例化这个模型，就不包装到外面的去了"""
    def train_model(self, X_train, y_train, param, X_valid=None, y_valid=None, stage='no_draw'):
        if self.model_select == 'XgbRegModel':
            dtrain = xgb.DMatrix(X_train, y_train)
            dvalid = xgb.DMatrix(X_valid, y_valid)
            eval_result = {}
            num_boost_round = int(param.pop('num_boost_round'))
            # if 'roll' not in period:
            model = xgb.train(param, dtrain,
                              num_boost_round=num_boost_round,
                              evals=[(dtrain, 'train'), (dvalid, 'valid')],
                              evals_result=eval_result,
                              verbose_eval=0,
                              obj=loss_fun1)
            # else:
            #     model_fpath = self.pred_out_path + f'model/{period.replace("_roll", "")}/seed_0/XgbRegModel.pkl'
            #     model = xgb.Booster(model_file=model_fpath)
            #     model.update(dtrain=dtrain, iteration=200)
            # if not hyper_search_mode and stage is 'draw':
                # lgb.plot_metric(eval_result, metric='rmse')
                # plt.savefig(self.eval_path + f'auc_{period}.png', bbox_inches='tight', pad_inches=0.0)
                # lgb.plot_metric(eval_result, metric='auc')
                # plt.savefig(self.eval_path + f'logloss_{period}.png', bbox_inches='tight', pad_inches=0.0)
            self.model = model
        elif self.model_select == 'LgbRegModel':
            dtrain = lgb.Dataset(X_train, y_train)
            dvalid = lgb.Dataset(X_valid, y_valid, reference=dtrain)
            eval_result = {}
            # if 'roll' not in period:
            model = lgb.train(param, dtrain,
                              valid_sets=[dtrain, dvalid],
                              evals_result=eval_result,
                              verbose_eval=0)
            # else:
            #     model_fpath = self.pred_out_path + f'model/{period.replace("_roll", "")}/seed_0/LgbRegModel.pkl'
            #     model = lgb.Booster(model_file=model_fpath)
            #     model = model.update(train_set=dtrain)
            # if not hyper_search_mode and stage is 'draw':
            #     lgb.plot_metric(eval_result, metric='auc')
            #     plt.savefig(self.eval_path + f'auc_{period}.png')
            #     lgb.plot_metric(eval_result, metric='binary_logloss')
            #     plt.savefig(self.eval_path + f'logloss_{period}.png', bbox_inches='tight', pad_inches=0.0)
            self.model = model
        # if self.model_select == 'Lr':
        elif self.model_select == 'MlpRegModel':
            param.update({'gpu_id': gpu_id})
            model = MlpRegModel(**param)
            model.train(X_train.values, y_train.values, X_valid.values, y_valid.values)
            self.model = model


    def predict(self, X_other):
        if self.model_select in ['XgbRegModel', 'LgbRegModel', 'LrRegModel']:
            _y_pred = self.model.predict(X_other)
        elif self.model_select == 'MlpRegModel':
            _y_pred = self.model.predict(X_other.values)
        else:
            raise Exception('输入模型错误！！！')
        return _y_pred

    def model_eval(self, y_true, y_pred, score_threshold=0.0, stage='test'):
        y_true_label = y_true.values.reshape(-1) > 0
        y_pred_label = y_pred > score_threshold
        fpr, tpr, th = roc_curve(y_true_label, y_pred, pos_label=1)

        # 绘制ROC曲线，可以尝试根据fpr序列中间那个数的值进行参与率的选取
        # if not hyper_search_mode and stage != 'no_draw':
        #     import matplotlib.pyplot as plt
        #     plt.figure(figsize=(15, 15))
        #     plt.plot(fpr, tpr, lw=5, label='')
        #     plt.plot([0, 1], [0, 1], '--', lw=5, color='grey', label=f'AUC={round(auc(fpr, tpr), 3)}')
        #     plt.axis('square')
        #     plt.xlim([0, 1])
        #     plt.ylim([0, 1])
        #     plt.xlabel('False Positive Rate', fontsize=20)
        #     plt.ylabel('True Positive Rate', fontsize=20)
        #     plt.title('ROC Curve', fontsize=25)
        #     plt.legend(loc='lower right', fontsize=20)
        #     plt.savefig(self.eval_path + f'roc_curve_{period}_{stage}.png', bbox_inches='tight', pad_inches=0.0)

        eval_auc = auc(fpr, tpr)
        eval_accuracy = float(np.mean(y_true_label == y_pred_label))
        eval_precision = float(np.mean(y_true_label[y_pred_label == 1]))
        eval_recall = float(np.mean(y_pred_label[y_true_label == 1]))
        eval_rmse = ((y_true.values[:, 0] - y_pred) ** 2).mean() ** 0.5
        eval_ic = pd.DataFrame([y_true.values.reshape(-1), y_pred]).T.corr('spearman').iloc[0, 1]
        return eval_auc, eval_accuracy, eval_precision, eval_recall, eval_rmse, eval_ic, y_pred_label

    def train_and_eval_model(self, param):
        X_train, X_test = self.X_train.copy(), self.X_test.copy()
        y_train, y_test = self.y_train.copy(), self.y_test.copy()

        if scaler_select == 'scaler1':
            X_train_scaled, X_test_scaled = self.func_trans_train_test_scaler1(X_train, X_test)
        elif scaler_select == 'scaler2':
            X_train_scaled, X_test_scaled = self.func_trans_train_test_scaler2(X_train, X_test)

        self.train_model(X_train_scaled, y_train, param.copy(), X_valid=X_test_scaled, y_valid=y_test, stage='no_draw')
        dtest = self.wrap_test_data(X_test_scaled)
        y_test_pred = self.predict(dtest)

        eval_auc, eval_precision, eval_recall, eval_rmse, eval_ic, y_pred_label = self.model_eval(y_test, y_test_pred, score_threshold=self.best_threshold, stage='no_draw')
        print(f'该参数下表现均值为：{round(eval_auc, 4)}, {round(eval_precision, 4)}, {round(eval_recall, 4)}, {round(eval_rmse, 4)}, {round(eval_ic, 4)}')
        return eval_auc, eval_precision, eval_recall, eval_rmse, eval_ic

    @staticmethod
    def tranfrom_pred_data(y_test_pred, index, score_threshold=0.0):
        test_pred = list(y_test_pred > score_threshold)
        test_pred_prob = list(y_test_pred)
        test_pred_df = pd.DataFrame(index=index)
        test_pred_df['prediction'] = test_pred
        test_pred_df['pred_Reg'] = test_pred_prob
        test_pred_df['stockID'] = test_pred_df.index.get_level_values(1)
        test_pred_df['datelist'] = test_pred_df.index.get_level_values(0).strftime('%Y%m%d')

        test_pred_df['Indexs'] = test_pred_df['stockID'] + ' ' + test_pred_df['datelist']
        test_pred_df = test_pred_df.set_index('Indexs', drop=True)
        return test_pred_df

    def wrap_test_data(self, X_test):
        if self.model_select == 'XgbRegModel':
            return xgb.DMatrix(X_test)
        elif self.model_select == 'LgbRegModel':
            return X_test
        elif self.model_select == 'MlpRegModel':
            return X_test

    def start_train(self, param):
        param_copy = param.copy()

        self.get_train_and_test_data()

        if scaler_select == 'scaler1':
            X_train_scaled, X_test_scaled = self.func_trans_train_test_scaler1(self.X_train, self.X_test)
        elif scaler_select == 'scaler2':
            X_train_scaled, X_test_scaled = self.func_trans_train_test_scaler2(self.X_train, self.X_test)
        self.train_model(X_train_scaled, self.y_train, param_copy, X_test_scaled, self.y_test, stage='draw')

        dtrain = self.wrap_test_data(X_train_scaled)
        y_train_pred = self.predict(dtrain)
        train_auc, train_accuracy, train_precision, train_recall, train_rmse, train_ic, y_train_pred_label = self.model_eval(self.y_train, y_train_pred, score_threshold=self.best_threshold, stage='train')
        print(f'train区间结果：{round(train_auc, 4)}, {round(train_accuracy, 4)}, {round(train_precision, 4)}, {round(train_recall, 4)}, {round(train_rmse, 4)}')

        dtest = self.wrap_test_data(X_test_scaled)
        y_test_pred = self.predict(dtest)
        if seed == 0 and not period.endswith('roll'):
            self.best_threshold = np.percentile(y_test_pred, 100 - self.attend_ratio)
        else:
            self.best_threshold = pd.read_json(f'/data/user/015614/Zeus/pred/Europa/v4_0_86/{config_flag}/{self.model_name}/model/{period.replace("_roll", "")}/seed_0/_score_threshold.json').iloc[0, 0]
        test_auc, test_accuracy, test_precision, test_recall, test_rmse, test_ic, y_test_pred_label = self.model_eval(self.y_test, y_test_pred, score_threshold=self.best_threshold, stage='test')
        print(f'test区间结果：{round(test_auc, 4)}, {round(test_accuracy, 4)}, {round(test_precision, 4)}, {round(test_recall, 4)}, {round(test_rmse, 4)}')
        self.y_test_pred = y_test_pred

        if scaler_select == 'scaler1':
            X_fit_scaled = self.func_trans_train_test_with_scaler1(self.X_fit, self.scaler)
        elif scaler_select == 'scaler2':
            X_fit_scaled = self.func_trans_train_test_with_scaler2(self.X_fit, self.scaler)
        X_fit_scaled = pd.DataFrame(X_fit_scaled, index=self.X_fit.index, columns=self.X_fit.columns)
        dfit = self.wrap_test_data(X_fit_scaled)
        y_fit_pred = self.predict(dfit)
        fit_auc, fit_accuracy, fit_precision, fit_recall, fit_rmse, fit_ic, y_fit_pred_label = self.model_eval(self.y_fit, y_fit_pred, score_threshold=self.best_threshold, stage='fit')
        print(f'fit区间结果：{round(fit_auc, 4)}, {round(fit_accuracy, 4)}, {round(fit_precision, 4)}, {round(fit_recall, 4)}, {round(fit_rmse, 4)}')
        self.y_fit_pred = y_fit_pred

        return test_auc, ((test_auc, test_accuracy, test_precision, test_recall, test_rmse, test_ic),
                         (fit_auc, fit_accuracy, fit_precision, fit_recall, fit_rmse, fit_ic),
                          (train_auc, train_accuracy, train_precision, train_recall, train_rmse, train_ic))

inst = MyModelTrain(model_select=model_select)

if hyper_search_mode == 1:
    my_logger = MyLogger(strategy_name=inst.strategy_name, model_name=inst.model_name, version=inst.version, period=period).get_logger()
    my_logger.info(f'{inst.strategy_name} {inst.version} {inst.model_name}')
else:
    my_logger = None

# btl = BTLite2(strategy_name='Europa',
#               model_name='SingleTestModel',
#               date_dict=date_config[f'{period}'],
#               bt_save_path=junk_path + '回测结果/',
#               test_fpath=None,
#               fit_fpath=None)

def calc_stats_df(stats_df, stats_df2, model_test_mingan, model_fit_mingan):
    stats_df['平均收益风险比'] = model_test_mingan['收益风险比'].mean()
    stats_df['平均收益夏普比率'] = model_test_mingan['收益夏普比率'].mean()
    # stats_df['累计扣费总收益'] /= 1e8
    # stats_df['最大回撤'] /= 1e8
    # stats_df = stats_df.map(lambda x: round(x, 2))
    stats_df['基础样本数量'] = int(stats_df['基础样本数量'])
    stats_df['因子数量'] = len(inst.factor_list)

    stats_df2['平均收益风险比'] = model_fit_mingan['收益风险比'].mean()
    stats_df2['平均收益夏普比率'] = model_fit_mingan['收益夏普比率'].mean()
    # stats_df2['累计扣费总收益'] /= 1e8
    # stats_df2['最大回撤'] /= 1e8
    stats_df = stats_df.map(lambda x: round(x, 2))
    stats_df2['基础样本数量'] = int(stats_df2['基础样本数量'])

    print(stats_df[['收益风险比', '收益夏普比率', '平均收益风险比', '平均收益夏普比率', '累计扣费总收益', '最大回撤', '预测值与标签IC', '扣费后收益率胜率', '基础样本数量', '因子数量']].to_dict())
    stats_df = stats_df[['因子数量', '基础样本数量', '平均收益风险比', '平均收益夏普比率', '累计扣费总收益', '最大回撤', '样本参与率', '收益风险比', '夏普比率', '收益夏普比率', '预测值与标签IC']]
    stats_df2 = stats_df2[['基础样本数量', '平均收益风险比', '平均收益夏普比率', '累计扣费总收益', '最大回撤', '样本参与率', '收益风险比', '夏普比率', '收益夏普比率', '预测值与标签IC']]
    stats_df2 = stats_df2.rename(dict(zip(stats_df2.index.tolist(), [x + '_fit' for x in stats_df2.index])))

    stats_df = pd.concat([stats_df, stats_df2])
    output_dict = {'汇总结果': stats_df, 'test': model_test_mingan, 'fit': model_fit_mingan}
    return output_dict

def tuning_params(hyper_params_list, in_time=True, multi=True):
    def wrapper(params):
        for param in tqdm(params):
            valid_auc, eval_tuple = inst.start_train(param)
            inst.hyper_pred_out_path = inst.pred_out_path + f'hyper/{inst.search_time}/'

            y_test_pred_df = inst.tranfrom_pred_data(inst.y_test_pred, index=inst.y_test.index, score_threshold=inst.best_threshold)
            FileUtil.save_df2csv(y_test_pred_df, inst.hyper_pred_out_path, inst.test_pred_fname, verbose=False)

            y_fit_pred_df = inst.tranfrom_pred_data(inst.y_fit_pred, index=inst.y_fit.index, score_threshold=inst.best_threshold)
            FileUtil.save_df2csv(y_fit_pred_df, inst.hyper_pred_out_path, inst.fit_pred_fname, verbose=False)

            with open(inst.hyper_pred_out_path + 'param.json', 'w') as f_obj:
                json.dump(param, f_obj)

            with open(inst.hyper_pred_out_path + 'train_result.json', 'w') as f_obj:    # 保存train、test、fit的结果
                json.dump(eval_tuple, f_obj)

            if in_time:
                sbt = SimBackTest(pred_fpath_list=[y_test_pred_df],
                                  fit_fpath_list=[y_fit_pred_df],
                                  data_fpath=data_fpath,
                                  period=period,
                                  profit_data_fpath=profit_data_fpath,
                                  date_dict=DATE_CONFIG[period],
                                  attend_ratio_range=(10, 50),
                                  save_flag=False,
                                  multi_attend=True)
                stats_df, stats_df2, model_test_mingan, model_fit_mingan = sbt.start_backtest(multi=False)
                stats_dict = calc_stats_df(stats_df, stats_df2, model_test_mingan, model_fit_mingan)
                FileUtil.save_dict2xls(stats_dict, inst.hyper_pred_out_path, f'bt_result_{period}.xlsx', verbose=False)

            # watch_scores = {
            #     'test_auc': eval_tuple[0][0],
            #     'test_precision': eval_tuple[0][1],
            #     'test_recall': eval_tuple[0][2],
            #     'test_rmse': eval_tuple[0][3],
            #     'test_ic': eval_tuple[0][4],
            #     'fit_auc': eval_tuple[1][0],
            #     'fit_precision': eval_tuple[1][1],
            #     'fit_recall': eval_tuple[1][2],
            #     'fit_rmse': eval_tuple[1][3],
            #     'fit_ic': eval_tuple[1][4],
            #     # 'test_收益夏普比率': model_test_mingan['收益夏普比率'].mean(),
            #     # 'test_收益风险比': model_test_mingan['收益风险比'].mean(),
            #     # 'fit_收益夏普比率': model_fit_mingan['收益夏普比率'].mean(),
            #     # 'fit_收益风险比': model_fit_mingan['收益风险比'].mean(),
            # }
                stats_dict['param'] = str(param)

                watch_scores = stats_df[['收益风险比', '收益夏普比率', '平均收益风险比', '平均收益夏普比率', '累计扣费总收益', '最大回撤', '基础样本数量', '扣费后收益率胜率']].to_dict()

                my_logger.info(f'num_boost_round: {param["num_boost_round"]} | seed: {param["seed"]}: {watch_scores}')
            else:
                inst.search_time += 1

    param_list = list()
    for param_dict in hyper_params_list:
        for seed in range(2000, 2005):  # 设置5个随机种子，然后取结果的平均，稳定波动
            param_dict['seed'] = seed
            param_list.append(param_dict.copy())

    wrapper(param_list)
    return


if hyper_search_mode == 1:
    if model_select == 'XgbRegModel':
        tuning_params(hyper_xgb_reg_params_list, in_time=False)
    elif model_select == 'LgbRegModel':
        tuning_params(hyper_lgb_reg_params_list, in_time=False)
elif hyper_search_mode == 2:
    if model_select == 'XgbRegModel':
        tuning_params(hyper2_xgb_reg_params_list, in_time=False)
    elif model_select == 'LgbRegModel':
        tuning_params(hyper2_lgb_reg_params_list, in_time=False)
elif hyper_search_mode == 0:   # 此时才保存模型
    valid_auc, eval_tuple = inst.start_train(inst.param)

    y_test_pred_df = inst.tranfrom_pred_data(inst.y_test_pred, index=inst.y_test.index, score_threshold=inst.best_threshold)
    FileUtil.save_df2csv(y_test_pred_df, inst.pred_out_path, inst.test_pred_fname, verbose=False)

    y_fit_pred_df = inst.tranfrom_pred_data(inst.y_fit_pred, index=inst.y_fit.index, score_threshold=inst.best_threshold)
    FileUtil.save_df2csv(y_fit_pred_df, inst.pred_out_path, inst.fit_pred_fname, verbose=False)

    sbt = SimBackTest(pred_fpath_list=[inst.pred_out_path + '/' + inst.test_pred_fname],
                      fit_fpath_list=[inst.pred_out_path + '/' + inst.fit_pred_fname],
                      date_dict=DATE_CONFIG[period],
                      data_fpath=data_fpath,
                      period=period,
                      profit_data_fpath=profit_data_fpath,
                      attend_ratio_range=(20, 50),
                      save_flag=False,
                      multi_attend=True)
    stats_df, stats_df2, model_test_mingan, model_fit_mingan = sbt.start_backtest(multi=False)
    stats_dict = calc_stats_df(stats_df, stats_df2, model_test_mingan, model_fit_mingan)
    if seed == 0:
        FileUtil.save_dict2xls(stats_dict, inst.pred_out_path, f'bt_result_{period}.xlsx')

    """保存模型"""
    if inst.model_select in ['XgbRegModel', 'LgbRegModel']:
        os.makedirs(model_save_path + f'{inst.prefix_path}/model/{period}/seed_{seed}/', exist_ok=True)
        model_path = model_save_path + f'{inst.prefix_path}/model/{period}/seed_{seed}/'
        inst.model.save_model(model_path + f'{inst.model_select}.pkl')
        with open(model_path + '_factorName.json', 'w') as f:
            json.dump(inst.factor_list, f, ensure_ascii=False, indent=2)

        factor_scaler_info = pd.DataFrame()
        factor_scaler_info['factorName'] = inst.factor_list

        if scaler_select == 'scaler1':
            factor_scaler_info['n'] = inst.scaler[0]
            factor_scaler_info['median'] = list(inst.scaler[1])
            factor_scaler_info['mad'] = list(inst.scaler[2])
            factor_scaler_info['train_min'] = list(inst.scaler[3])
            factor_scaler_info['train_max'] = list(inst.scaler[4])
        elif scaler_select == 'scaler2':
            factor_scaler_info['std'] = list(inst.scaler[0])
            factor_scaler_info['mean'] = list(inst.scaler[1])

        # 保存scaler结果
        factor_scaler_info.to_json(model_path + '_factorScaler.json', orient='records', lines=False, double_precision=15)
        # 保存因子列表名称
        factor_scaler_info['factorName'].to_json(model_path + '_factorName.json', orient='values')
        # 保存最佳阈值和scaler名字
        pd.Series([inst.best_threshold, scaler_select]).to_json(model_path + '_score_threshold.json', orient='records', lines=False, double_precision=15)

        FileUtil.save_df2csv(y_test_pred_df, model_path, inst.test_pred_fname, verbose=False)
        FileUtil.save_df2csv(y_fit_pred_df, model_path, inst.fit_pred_fname, verbose=False)
        FileUtil.save_dict2xls(stats_dict, model_path, f'bt_result_{period}.xlsx')