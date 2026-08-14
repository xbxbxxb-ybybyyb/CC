# coding: utf-8
# Author：fengchi863
# Date ：2023/8/16 10:29

import sys
sys.path.append('/data/user/015614/Lucien')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
from Zeus.Metis.v1_0_7.path_conf import *
from Zeus.Metis.v1_0_7.hyper_param_space import *
import xgboost as xgb
import lightgbm as lgb
from sklearn.metrics import roc_curve, auc
from LucienUtil.FileUtil import FileUtil
from Zeus.Metis.v1_0_7.my_logger import MyLogger
import warnings
import random
import os
gpu_id = random.randint(0, 2)
os.environ['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
import json
import joblib
import time
import sys
np.random.seed(2008)
warnings.filterwarnings("ignore")

"""确定选用的区间、因子筛选、标签、模型、是否超参数寻优"""
if len(sys.argv) > 1:
    period = sys.argv[1]
    fs_version = sys.argv[2]
    label_flag = sys.argv[3]
    model_select = sys.argv[4]
    hyper_search_mode = eval(sys.argv[5])
    attend_ratio = int(sys.argv[6])
else:
    period = 'period1'
    fs_version = 'rffs' # fsv8\fsv10\fsv11\rffs
    label_flag = 'pct'
    model_select = 'LgbRegModel'
    hyper_search_mode = False
    attend_ratio = 30
print(period, fs_version, label_flag, model_select, hyper_search_mode, attend_ratio)

"""确定选用的超参数"""
if model_select == 'XgbRegModel':
    hyper_params = hyper_xgb_reg_params
elif model_select == 'LgbRegModel':
    hyper_params = hyper_lgb_reg_params
elif model_select == 'LrRegModel':
    hyper_params = hyper_lr_reg_params
else:
    raise Exception('模型名字输入错误！！！')


"""
model_name: like fsv8_pct_XgbRegModel...
model: like XgbRegModel...
version: like v1_0_0...
strategy_name: like Europa, Jupiter...
"""
class MyModelTrain:
    def __init__(self, model_select='XgbRegModel'):
        self.model_name = f'{fs_version}_{label_flag}_{model_select}'
        self.model_select = model_select
        self.strategy_name = 'Metis'
        self.version = 'v1_0_7'
        self.attend_ratio = attend_ratio
        self.best_threshold = 0
        self.prefix_path = f'{self.strategy_name}/{self.version}/{self.model_name}/'

        self.pred_out_path = pred_out_path + self.prefix_path
        self.bt_out_path = bt_out_path + f'{self.strategy_name}/{self.version}/'
        self.factor_path = factor_path + self.prefix_path
        self.log_path = log_path + self.prefix_path
        self.eval_path = pred_out_path + self.prefix_path + 'eval/'
        self.hyper_pred_out_path = None
        self.create_floders()

        # 设置参数和阈值
        self.param = {}
        # TODO：如果没有寻优参数文件，那就填写万能参数
        if not hyper_search_mode:
            if os.path.exists(self.log_path + f'{self.strategy_name}_{self.version}_{self.model_name}_{period}.xlsx'):
                self.param = pd.read_excel(self.log_path + f'{self.strategy_name}_{self.version}_{self.model_name}_{period}.xlsx', index_col=0).iloc[0]['整体参数']
            else:
                if self.model_select == 'XgbRegModel':
                    self.param = fixed_xgb_reg_param
                elif self.model_select == 'LgbRegModel':
                    self.param = fixed_lgb_reg_param
            print('最优参数: ', self.param)
        else:   # 寻优
            if self.model_select == 'XgbRegModel':
                self.param = hyper_xgb_reg_params
            elif self.model_select == 'LgbRegModel':
                self.param = hyper_lgb_reg_params
        self.param = eval(self.param)

        self.X, self.y = None, None
        self.model = None
        self.scaler = None
        self.label = label_config[label_flag]

        self.factor_list = None
        self.search_time = 0
        self.date_dict = date_config[f'{period}']
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

    def select_factor(self):
        if fs_version in ['fsv8', 'fsv10', 'fsv11']:
            xgb_imptc_fpath = eval(f'xgb_imptc_{label_flag}_{fs_version}_{period}_fpath')
            filter_factor_df = pd.read_excel(xgb_imptc_fpath, index_col=0)
            _xgb_imptc_factor = filter_factor_df.query('corr_selected==1')
            factor_list = _xgb_imptc_factor['factor_name'].tolist()
        elif fs_version == 'fsrs':
            factor_list = pd.read_excel(eval(f'fsrs_imptc_{label_flag}_{period}_fpath'), index_col=0)
            factor_list = factor_list.query('select == 1')['factor_name'].tolist()
        else:
            try:
                factor_list = pd.read_pickle(eval(fs_config[fs_version]))
            except:
                raise Exception('因子筛选输入错误！！！')
        print(f'{period} {label_flag} | use {fs_version} which includes {len(factor_list)} factors and use No.{gpu_id} GPU')
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

    """根据model名字选择实例化这个模型，就不包装到外面的去了"""
    def train_model(self, X_train, y_train, param, X_valid=None, y_valid=None, stage='no_draw'):
        if self.model_select == 'XgbRegModel':
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
                lgb.plot_metric(eval_result, metric='rmse')
                plt.savefig(self.eval_path + f'auc_{period}.png', bbox_inches='tight', pad_inches=0.0)
                # lgb.plot_metric(eval_result, metric='auc')
                # plt.savefig(self.eval_path + f'logloss_{period}.png', bbox_inches='tight', pad_inches=0.0)
            self.model = model
        elif self.model_select == 'LgbRegModel':
            dtrain = lgb.Dataset(X_train, y_train)
            dvalid = lgb.Dataset(X_valid, y_valid, reference=dtrain)
            eval_result = {}
            model = lgb.train(param, dtrain,
                              valid_sets=[dtrain, dvalid],
                              evals_result=eval_result,
                              verbose_eval=0)
            if not hyper_search_mode and stage is 'draw':
                lgb.plot_metric(eval_result, metric='auc')
                plt.savefig(self.eval_path + f'auc_{period}.png')
                lgb.plot_metric(eval_result, metric='binary_logloss')
                plt.savefig(self.eval_path + f'logloss_{period}.png', bbox_inches='tight', pad_inches=0.0)
            self.model = model

    def predict(self, X_other):
        if self.model_select in ['XgbRegModel', 'LgbRegModel', 'LrRegModel']:
            _y_pred = self.model.predict(X_other)
        else:
            raise Exception('输入模型错误！！！')
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
            plt.savefig(self.eval_path + f'roc_curve_{period}_{stage}.png', bbox_inches='tight', pad_inches=0.0)

        eval_auc = auc(fpr, tpr)
        eval_precision = float(np.mean(y_true_label[y_pred_label == 1]))
        eval_recall = float(np.mean(y_pred_label[y_true_label == 1]))
        eval_rmse = ((y_true.values[:, 0] - y_pred) ** 2).mean() ** 0.5
        eval_ic = pd.DataFrame([y_true.values.reshape(-1), y_pred]).T.corr('spearman').iloc[0, 1]
        return eval_auc, eval_precision, eval_recall, eval_rmse, eval_ic, y_pred_label

    def train_and_eval_model(self, param):
        X_train, X_test = self.X_train.copy(), self.X_test.copy()
        y_train, y_test = self.y_train.copy(), self.y_test.copy()

        X_train_scaled, X_test_scaled = self.func_trans_train_test_minmaxmadscaler(X_train, X_test)

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

        #TODO: delete this """转换成买入日期"""
        test_pred_df['stockID'] = test_pred_df['stockID'] + test_pred_df.index.get_level_values(2).astype(int).astype(str)

        test_pred_df['Indexs'] = test_pred_df['stockID'] + ' ' + test_pred_df['datelist']
        test_pred_df = test_pred_df.set_index('Indexs', drop=True)
        return test_pred_df

    def wrap_test_data(self, X_test):
        if self.model_select == 'XgbRegModel':
            return xgb.DMatrix(X_test)
        elif self.model_select == 'LgbRegModel':
            return X_test

    def start_train(self, param):
        param_copy = param.copy()

        self.get_train_and_test_data()

        X_train_scaled, X_test_scaled = self.func_trans_train_test_minmaxmadscaler(self.X_train, self.X_test)
        self.train_model(X_train_scaled, self.y_train, param_copy, X_test_scaled, self.y_test, stage='draw')

        dtest = self.wrap_test_data(X_test_scaled)
        y_test_pred = self.predict(dtest)
        self.best_threshold = np.percentile(y_test_pred, 100 - self.attend_ratio)
        test_auc, test_precision, test_recall, test_rmse, test_ic, y_test_pred_label = self.model_eval(self.y_test, y_test_pred, score_threshold=self.best_threshold, stage='test')
        print(f'test区间结果：{round(test_auc, 4)}, {round(test_precision, 4)}, {round(test_recall, 4)}, {round(test_rmse, 4)}')
        self.y_test_pred = y_test_pred

        X_fit_scaled = self.func_trans_train_test_with_scaler(self.X_fit, self.scaler)
        X_fit_scaled = pd.DataFrame(X_fit_scaled, index=self.X_fit.index, columns=self.X_fit.columns)
        dfit = self.wrap_test_data(X_fit_scaled)
        y_fit_pred = self.predict(dfit)
        fit_auc, fit_precision, fit_recall, fit_rmse, fit_ic, y_fit_pred_label = self.model_eval(self.y_fit, y_fit_pred, score_threshold=self.best_threshold, stage='fit')
        print(f'fit区间结果：{round(fit_auc, 4)}, {round(fit_precision, 4)}, {round(fit_recall, 4)}, {round(fit_rmse, 4)}')
        self.y_fit_pred = y_fit_pred

        return test_auc, ((test_auc, test_precision, test_recall, test_rmse, test_ic),
                         (fit_auc, fit_precision, fit_recall, fit_rmse, fit_ic))

inst = MyModelTrain(model_select=model_select)

if hyper_search_mode:
    my_logger = MyLogger(strategy_name=inst.strategy_name, model_name=inst.model_name, version=inst.version, period=period).get_logger()
    my_logger.info(f'{inst.strategy_name} {inst.version} {inst.model_name}')
else:
    my_logger = None

# btl = BTLite2(strategy_name='Metis',
#               model_name='SingleTestModel',
#               date_dict=date_config[f'{period}'],
#               bt_save_path=junk_path + '回测结果/',
#               test_fpath=None,
#               fit_fpath=None)

def tuning_params(param):
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
        'test_auc': eval_tuple[0][0],
        'test_precision': eval_tuple[0][1],
        'test_recall': eval_tuple[0][2],
        'test_rmse': eval_tuple[0][3],
        'test_ic': eval_tuple[0][4],
        'fit_auc': eval_tuple[1][0],
        'fit_precision': eval_tuple[1][1],
        'fit_recall': eval_tuple[1][2],
        'fit_rmse': eval_tuple[1][3],
        'fit_ic': eval_tuple[1][4],
        # 'test_收益夏普比率': model_test_mingan['收益夏普比率'].mean(),
        # 'test_收益风险比': model_test_mingan['收益风险比'].mean(),
        # 'fit_收益夏普比率': model_fit_mingan['收益夏普比率'].mean(),
        # 'fit_收益风险比': model_fit_mingan['收益风险比'].mean(),
    }

    my_logger.info(f'{watch_scores}: {param}')
    inst.search_time += 1

    return -valid_auc


if hyper_search_mode:
    max_evals = 10
    for idx in range(max_evals):
        if model_select == 'XgbRegModel':
            auc_indicator = tuning_params(hyper_xgb_reg_params)
            hyper_xgb_reg_params['num_boost_round'] -= 20
        elif model_select == 'LgbRegModel':
            auc_indicator = tuning_params(hyper_lgb_reg_params)
            hyper_lgb_reg_params['n_estimators'] -= 20
    my_logger.info(f'超参数寻优结束，最优超参数为{hyper_xgb_reg_params}')
else:
    valid_auc, eval_tuple = inst.start_train(inst.param)

    y_test_pred_df = inst.tranfrom_pred_data(inst.y_test_pred, index=inst.y_test.index, score_threshold=inst.best_threshold)
    FileUtil.save_df2csv(y_test_pred_df, inst.pred_out_path, inst.test_pred_fname)

    y_fit_pred_df = inst.tranfrom_pred_data(inst.y_fit_pred, index=inst.y_fit.index, score_threshold=inst.best_threshold)
    FileUtil.save_df2csv(y_fit_pred_df, inst.pred_out_path, inst.fit_pred_fname)

    """保存模型"""
    if inst.model_select in ['XgbRegModel', 'LgbRegModel']:
        os.makedirs(model_save_path + f'{inst.prefix_path}/model/{period}/', exist_ok=True)
        model_path = model_save_path + f'{inst.prefix_path}/model/{period}/'
        inst.model.save_model(model_path + f'{inst.model_select}.pkl')
        with open(model_path + '_factorName.json', 'w') as f:
            json.dump(inst.factor_list, f, ensure_ascii=False, indent=2)

        factor_scaler_info = pd.DataFrame()
        factor_scaler_info['factorName'] = inst.factor_list
        factor_scaler_info['n'] = inst.scaler[0]
        factor_scaler_info['median'] = list(inst.scaler[1])
        factor_scaler_info['mad'] = list(inst.scaler[2])
        factor_scaler_info['train_min'] = list(inst.scaler[3])
        factor_scaler_info['train_max'] = list(inst.scaler[4])
        factor_scaler_info.to_json(model_path + '_factorScaler.json', orient='records', lines=False, double_precision=15)
        factor_scaler_info['factorName'].to_json(model_path + '_factorName.json', orient='values')
        with open(model_path + '_score_threshold.json', 'w') as f:
            json.dump([inst.best_threshold], f, ensure_ascii=False, indent=2)