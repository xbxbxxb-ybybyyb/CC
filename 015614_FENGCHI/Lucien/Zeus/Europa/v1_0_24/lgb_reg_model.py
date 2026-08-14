# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 8:47
import sys
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import numpy as np
from Zeus.Europa.v1_0_24.path_conf import *
from Zeus.Europa.v1_0_24.hyper_param_space import hyper_lgb_reg_params
from model_eval.bak.bak20230105_simple_bt.v3_6_SimpleEvalLaunch import EvalLaunch
from lightgbm import LGBMRegressor
from LucienUtil.FileUtil import FileUtil
from Zeus.Europa.v1_0_24.my_logger import MyLogger
import warnings
import os
import random
random.seed(2023)
warnings.filterwarnings("ignore")

PERIOD = 'period4'
SUB_VERSION = 'v4'

# 开始正式训练
hyper_search_mode = False
fit_cheat_mode = False
use_test_param_mode = False

# param_test = {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.7000000000000001, 'device': 'gpu', 'factor_num': 290.0, 'gpu_device_id': 0, 'gpu_platform_id': 1, 'learning_rate': 0.005, 'max_depth': 4.0, 'min_child_samples': 10.0, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 1400.0, 'n_jobs': -1, 'num_leaves': 16.0, 'random_state': 2022, 'reg_alpha': 1.0, 'reg_lambda': 0.8, 'score_threshold': 0.00291, 'silent': True, 'subsample': 0.6000000000000001, 'subsample_freq': 0}
# param_test = {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.7000000000000001, 'device': 'gpu', 'factor_num': 290.0, 'gpu_device_id': 0, 'gpu_platform_id': 1, 'learning_rate': 0.005, 'max_depth': 3.0, 'min_child_samples': 4.0, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 1400.0, 'n_jobs': -1, 'num_leaves': 36.0, 'random_state': 2022, 'reg_alpha': 0.6000000000000001, 'reg_lambda': 0.8, 'score_threshold': 0.001461, 'silent': True, 'subsample': 0.9, 'subsample_freq': 0}
param_test = {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.7000000000000001, 'device': 'gpu', 'factor_num': 290.0, 'gpu_device_id': 0, 'gpu_platform_id': 1, 'learning_rate': 0.005, 'max_depth': 3.0, 'min_child_samples': 4.0, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 1400.0, 'n_jobs': -1, 'num_leaves': 36.0, 'random_state': 2022, 'reg_alpha': 0.6000000000000001, 'reg_lambda': 0.8, 'score_threshold': 0.002089, 'silent': True, 'subsample': 0.9, 'subsample_freq': 0}
# param_fit = {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.7000000000000001, 'device': 'gpu', 'factor_num': 290.0, 'gpu_device_id': 0, 'gpu_platform_id': 1, 'learning_rate': 0.005, 'max_depth': 3.0, 'min_child_samples': 4.0, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 1400.0, 'n_jobs': -1, 'num_leaves': 36.0, 'random_state': 2022, 'reg_alpha': 0.6000000000000001, 'reg_lambda': 0.8, 'score_threshold': 0.003987, 'silent': True, 'subsample': 0.9, 'subsample_freq': 0}
param_fit = {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.7000000000000001, 'device': 'gpu', 'factor_num': 290.0, 'gpu_device_id': 0, 'gpu_platform_id': 1, 'learning_rate': 0.005, 'max_depth': 3.0, 'min_child_samples': 4.0, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 1400.0, 'n_jobs': -1, 'num_leaves': 36.0, 'random_state': 2022, 'reg_alpha': 0.6000000000000001, 'reg_lambda': 0.8, 'score_threshold': 0.00225, 'silent': True, 'subsample': 0.9, 'subsample_freq': 0}
hyper_params = hyper_lgb_reg_params

param_test = {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.5, 'device': 'gpu', 'factor_num': 300.0, 'gpu_device_id': 0, 'gpu_platform_id': 1, 'learning_rate': 0.005, 'max_depth': 4.0, 'min_child_samples': 16.0, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 1400.0, 'n_jobs': -1, 'num_leaves': 12.0, 'random_state': 2022, 'reg_alpha': 0.5, 'reg_lambda': 0.8, 'score_threshold': 0.002061, 'silent': True, 'subsample': 0.9, 'subsample_freq': 0}

class LgbRegModel:
    def __init__(self, mode='test', sub_version='v1'):
        self.model_name = 'LgbRegModel'
        self.strategy_name = 'Europa'
        self.version = 'v1_0_24'
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

        self.get_dataset(data_test_fpath)

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

        y = pd.read_pickle('/data/group/800463/sunss/for_xly/europa/newProfit/LabelProfit_zt_twap_0.10_800_190_SH450_SZ100.pkl')
        y = y[[self.label]]
        y.columns = [self.label]

        y = y.reindex(index=X.index)

        # TODO：delete，20220101之后日期的label都赋值成了0
        y['trade_date'] = y.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
        y.loc[y['trade_date'] >= 20220101, self.label] = 0

        y = y.drop(np.isnan(y)[self.label][np.isnan(y)[self.label]].index)
        X = X.reindex(index=y.index)

        self.X = X
        self.y = y

    def filter_factor(self, xgb_imptc_fpath=xgb_imptc_fpath, factor_score_fpath=factor_score_fpath):
        filter_factor_df = pd.read_excel(xgb_imptc_fpath, index_col=0)
        _xgb_imptc_factor = filter_factor_df.query('corr_selected==1')
        factor_list = _xgb_imptc_factor['factor_name'].tolist()

        # import json
        # with open('/data/group/800463/fengc/for_wj/model_config/period4_FSV8_LgbRegModel/_factorName.json', 'r', encoding='utf-8') as f:
        #     _factor_list = json.load(f)

        self.factor_list = factor_list
        return factor_list

    def get_train_and_test_data(self):
        X_copy = self.X.copy()
        y_copy = self.y.copy()
        X_copy = X_copy.drop(X_copy.filter(regex='label*').columns.tolist(), axis=1)
        y_copy = y_copy.reindex(index=X_copy.index)

        filtered_factor = self.filter_factor()
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

        # minmax
        # X_train, X_valid, X_test = self.fun_trans_train_test_minmaxscaler(X_train, X_valid, X_test)
        X_train, X_valid, X_test = self.fun_trans_train_test_standardscaler(X_train, X_valid, X_test)

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

    def train_model(self, X_train, y_train, param):
        model = LGBMRegressor(**param)
        model.fit(X_train.values, y_train.values.ravel())
        # # TODO:delete, for test
        # import lightgbm
        # model = lightgbm.Booster(model_file=junk_path + 'period4_LgbRegModel.pkl')
        self.model = model

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
        if 'num_leaves' in param_copy.keys():
            param_copy['num_leaves'] = int(param_copy['num_leaves'])
        if 'min_data_in_leaf' in param_copy.keys():
            param_copy['min_data_in_leaf'] = int(param_copy['min_data_in_leaf'])
        if 'min_child_samples' in param_copy.keys():
            param_copy['min_child_samples'] = int(param_copy['min_child_samples'])

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


inst_test = LgbRegModel(mode='test', sub_version=SUB_VERSION)
inst_fit = LgbRegModel(mode='fit', sub_version=SUB_VERSION)
def tuning_params(param):
    pred_result = inst_test.start_train(param=param)
    inst_test.hyper_pred_out_path = inst_test.pred_out_path + f'hyper/{inst_test.search_time}/'
    FileUtil.save_df2csv(pred_result, inst_test.hyper_pred_out_path, inst_test.pred_fname)

    # 调用回测框架，后期可改为简短的回测
    eval_inst = EvalLaunch(date_config=inst_test.date_dict,
                           strategy_name=inst_test.strategy_name,
                           sel_model_names=[inst_test.model_name],
                           valid_path_list=[inst_test.hyper_pred_out_path + inst_test.pred_fname],
                           pred_path_list=[inst_test.hyper_pred_out_path + inst_test.pred_fname],
                           file_save_path=inst_test.hyper_pred_out_path,
                           save_flag=False)

    model_eval, model_inmingan, model_mingan, merge_attend_metric = eval_inst.launch()
    model_inmingan = model_inmingan.sort_values('收益风险比', ascending=False)
    model_inmingan['test_indicator'] = model_inmingan['收益风险比'] * model_inmingan['累计盈利']
    model_inmingan_copy = model_inmingan.copy()
    model_inmingan_copy['fit_indicator'] = model_inmingan_copy['收益风险比'] * model_inmingan_copy['扣费收益率胜率'] * model_inmingan_copy['实际参与率']
    model_inmingan_copy = model_inmingan_copy.query('0.2 < 实际参与率 < 0.4')
    model_inmingan_copy = model_inmingan_copy.sort_values(['fit_indicator'], ascending=False).iloc[0]
    in_adapt_score_threshold = model_inmingan_copy.name
    model_mingan_copy_ = model_mingan.loc[in_adapt_score_threshold]

    model_mingan = model_mingan.sort_values('收益风险比', ascending=False)
    model_mingan['test_indicator'] = model_mingan['收益风险比'] * model_mingan['累计盈利']
    model_mingan_copy = model_mingan.copy()
    model_mingan_copy['fit_indicator'] = model_mingan_copy['收益风险比'] * model_mingan_copy['扣费收益率胜率'] * model_mingan_copy['实际参与率']
    model_mingan_copy = model_mingan_copy.query('0.2 < 实际参与率 < 0.4')
    model_mingan_copy = model_mingan_copy.sort_values(['fit_indicator'], ascending=False).iloc[0]

    ic = round(model_eval.loc['预测值与标签RankIC'][0], 4) if model_eval.shape[0] > 0 else 0
    adapt_profit_risk_ratio = round(model_mingan_copy['收益风险比'], 4) if model_mingan_copy.shape[0] > 0 else 0
    adapt_winrate = round(model_mingan_copy['扣费收益率胜率'], 4) if model_mingan_copy.shape[0] > 0 else 0
    adapt_join_pct = round(model_mingan_copy['实际参与率'], 4) if model_mingan_copy.shape[0] > 0 else 0
    adapt_sharpe_ratio = round(model_mingan_copy['夏普比率'], 4) if model_mingan_copy.shape[0] > 0 else 0
    adapt_cum_profit = round(model_mingan_copy['累计盈利'], 4) if model_mingan_copy.shape[0] > 0 else 0
    adapt_score_threshold = float(model_mingan_copy.name) if model_mingan_copy.shape[0] > 0 else 0

    adapt_profit_risk_ratio_ = round(model_mingan_copy_['收益风险比'], 4) if model_mingan_copy_.shape[0] > 0 else 0
    adapt_winrate_ = round(model_mingan_copy_['扣费收益率胜率'], 4) if model_mingan_copy_.shape[0] > 0 else 0
    adapt_join_pct_ = round(model_mingan_copy_['实际参与率'], 4) if model_mingan_copy_.shape[0] > 0 else 0
    adapt_sharpe_ratio_ = round(model_mingan_copy_['夏普比率'], 4) if model_mingan_copy_.shape[0] > 0 else 0
    adapt_cum_profit_ = round(model_mingan_copy_['累计盈利'], 4) if model_mingan_copy_.shape[0] > 0 else 0
    adapt_score_threshold_ = in_adapt_score_threshold
    mean_profit_risk_ratio = round(merge_attend_metric.mean(axis=0).iloc[5], 4)
    mean_profit_sharp_ratio = round(merge_attend_metric.mean(axis=0).iloc[7], 4)
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
        '平均收益风险比': mean_profit_risk_ratio,
        '平均收益夏普比率': mean_profit_sharp_ratio,
    }
    param['score_threshold'] = float(adapt_score_threshold_)

    if fit_cheat_mode:
        pred_result = inst_fit.start_train(param=param)
        inst_fit.hyper_pred_out_path = inst_fit.pred_out_path + f'hyper/{inst_fit.search_time}/'
        FileUtil.save_df2csv(pred_result, inst_fit.hyper_pred_out_path, inst_fit.pred_fname)

        eval_inst = EvalLaunch(date_config=inst_fit.date_dict,
                               strategy_name=inst_fit.strategy_name,
                               sel_model_names=[inst_fit.model_name],
                               valid_path_list=[inst_fit.hyper_pred_out_path + inst_fit.pred_fname],
                               pred_path_list=[inst_fit.hyper_pred_out_path + inst_fit.pred_fname],
                               file_save_path=inst_fit.hyper_pred_out_path,
                               save_flag=False)
        model_eval, model_inmingan, model_mingan, merge_attend_metric = eval_inst.launch()

        model_inmingan = model_inmingan.sort_values('收益风险比', ascending=False)
        model_inmingan['test_indicator'] = model_inmingan['收益风险比'] * model_inmingan['累计盈利']
        model_inmingan_copy = model_inmingan.copy()
        model_inmingan_copy['fit_indicator'] = model_inmingan_copy['收益风险比'] * model_inmingan_copy['扣费收益率胜率'] * model_inmingan_copy['实际参与率']
        model_inmingan_copy = model_inmingan_copy.query('0.2 < 实际参与率 < 0.4')  # 控制参与率在0.1-0.3之间
        model_inmingan_copy = model_inmingan_copy.sort_values(['fit_indicator'], ascending=False).iloc[0]
        in_adapt_score_threshold = model_inmingan_copy.name
        model_mingan_copy_ = model_mingan.loc[in_adapt_score_threshold]

        model_mingan = model_mingan.sort_values('收益风险比', ascending=False)
        model_mingan_copy = model_mingan.copy()
        model_mingan_copy['fit_indicator'] = model_mingan_copy['收益风险比'] * model_mingan_copy['扣费收益率胜率'] * model_mingan_copy['实际参与率']
        model_mingan_copy = model_mingan_copy.query('0.2 < 实际参与率 < 0.4')  # 控制参与率在0.1-0.3之间
        model_mingan_copy = model_mingan_copy.sort_values(['fit_indicator'], ascending=False).iloc[0]

        _ic = round(model_eval.loc['预测值与标签IC'][0], 4) if model_eval.shape[0] > 0 else 0
        _sharpe_ratio = round(model_eval.loc['夏普比率'][0], 4) if model_eval.shape[0] > 0 else 0
        _buy_times = round(model_eval.loc['实际参与次数'][0], 4) if model_eval.shape[0] > 0 else 0
        _cum_profit = round(model_eval.loc['累计扣费总收益'][0], 4) if model_eval.shape[0] > 0 else 0
        _mdd_profit = round(model_eval.loc['最大回撤'][0], 4) if model_eval.shape[0] > 0 else 0
        _winrate = round(model_eval.loc['扣费后收益率胜率'][0], 4) if model_eval.shape[0] > 0 else 0
        _join_pct = round(model_eval.loc['样本参与率'][0], 4) if model_eval.shape[0] > 0 else 0
        _max_profit_risk_ratio = round(model_mingan['收益风险比'][0], 4) if model_mingan.shape[0] > 0 else 0
        _max_winrate = round(model_mingan['扣费收益率胜率'].max(), 4) if model_mingan.shape[0] > 0 else 0
        _max_cum_profit = round(model_mingan['累计盈利'].max(), 4) if model_mingan.shape[0] > 0 else 0
        _max_sharpe_ratio = round(model_mingan['夏普比率'].max(), 4) if model_mingan.shape[0] > 0 else 0
        _adapt_profit_risk_ratio = round(model_mingan_copy['收益风险比'], 4) if model_mingan_copy.shape[0] > 0 else 0
        _adapt_winrate = round(model_mingan_copy['扣费收益率胜率'], 4) if model_mingan_copy.shape[0] > 0 else 0
        _adapt_join_pct = round(model_mingan_copy['实际参与率'], 4) if model_mingan_copy.shape[0] > 0 else 0
        _adapt_sharpe_ratio = round(model_mingan_copy['夏普比率'], 4) if model_mingan_copy.shape[0] > 0 else 0
        _adapt_cum_profit = round(model_mingan_copy['累计盈利'], 4) if model_mingan_copy.shape[0] > 0 else 0
        _adapt_score_threshold = float(model_mingan_copy.name) if model_mingan_copy.shape[0] > 0 else 0
        # 根据样本内选出的阈值进行计算
        _adapt_profit_risk_ratio_ = round(model_mingan_copy_['收益风险比'], 4) if model_mingan_copy_.shape[0] > 0 else 0
        _adapt_winrate_ = round(model_mingan_copy_['扣费收益率胜率'], 4) if model_mingan_copy_.shape[0] > 0 else 0
        _adapt_join_pct_ = round(model_mingan_copy_['实际参与率'], 4) if model_mingan_copy_.shape[0] > 0 else 0
        _adapt_sharpe_ratio_ = round(model_mingan_copy_['夏普比率'], 4) if model_mingan_copy_.shape[0] > 0 else 0
        _adapt_cum_profit_ = round(model_mingan_copy_['累计盈利'], 4) if model_mingan_copy_.shape[0] > 0 else 0
        _adapt_score_threshold_ = in_adapt_score_threshold
        _mean_profit_risk_ratio = round(merge_attend_metric.mean(axis=0).iloc[5], 4)
        _mean_profit_sharp_ratio = round(merge_attend_metric.mean(axis=0).iloc[7], 4)

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
            '平均收益风险比2': _mean_profit_risk_ratio,
            '平均收益夏普比率2': _mean_profit_sharp_ratio,
        })

    my_logger.info(f'{watch_scores}: {param}')
    inst_test.search_time += 1

    return -ic


if hyper_search_mode or use_test_param_mode:
    my_logger = MyLogger(strategy_name=inst_test.strategy_name, model_name=inst_test.model_name, version=inst_test.version, sub_version=inst_test.sub_version).get_logger()
    my_logger.info(f'{inst_test.strategy_name} {inst_test.version} {inst_test.model_name} {inst_test.sub_version}')
else:
    my_logger = None

if hyper_search_mode:
    from hyperopt import fmin, Trials, tpe
    max_evals = 300
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

    # pred_result = inst_fit.start_train(param=param_fit)
    # FileUtil.save_df2csv(pred_result, inst_fit.pred_out_path, inst_fit.pred_fname)
    # check = pred_result.query('datelist >= "20220101" & prediction == True')

    # inst_fit.date_dict = dict(train_start_date=20160101, train_end_date=20211231, valid_start_date=20210401, valid_end_date=20211231, test_start_date=20211201, test_end_date=20220630)
    # inst_fit.pred_fname = 'prod_for_search_threshold.csv'
    # pred_result = inst_fit.start_train(param=param_fit)
    # import json
    # inst_fit.model.booster_.save_model(junk_path + 'period4_LgbRegModel.pkl')
    # with open(junk_path + '_factorName.json', 'w') as f:
    #     json.dump(inst_fit.factor_list, f, ensure_ascii=False, indent=2)
    #
    # factor_scaler_info = pd.DataFrame()
    # factor_scaler_info['factorName'] = inst_fit.factor_list
    # factor_scaler_info['min'] = list(inst_fit.scaler.data_min_)
    # factor_scaler_info['max'] = list(inst_fit.scaler.data_max_)
    # factor_scaler_info.to_json(junk_path + '_factorScaler.json', orient='records')
    # factor_scaler_info['factorName'].to_json(junk_path + '_factorName.json', orient='values')
    # with open(junk_path + '_score_threshold.json', 'w') as f:
    #     json.dump([param_fit['score_threshold']], f, ensure_ascii=False, indent=2)

    # FileUtil.save_df2csv(pred_result, inst_fit.pred_out_path, inst_fit.pred_fname)