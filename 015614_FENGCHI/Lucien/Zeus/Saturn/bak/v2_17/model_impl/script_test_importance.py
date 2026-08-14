# coding: utf-8
# Author：fengchi863

import warnings

import numpy as np
import pandas as pd
import time
from sklearn.linear_model import LogisticRegression, RidgeClassifier, RandomizedLogisticRegression
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
import xgboost as xgb
from minepy import MINE
import shap
from LucienUtil.FileUtil import FileUtil
from Zeus.Saturn.v2_17.DataPrepare import DataPrepare
from Zeus.Saturn.v2_17.hyper_param_space import model_params
from Zeus.Saturn.v2_17.models.xgb_reg_model import XGBRegModel
from Zeus.Saturn.v2_17.path_conf import *
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.feature_selection import RFE, f_regression

np.random.RandomState(2022)
warnings.filterwarnings('ignore')

strategy_name = 'SaturnS1'
version = 'v2_17'
model_name = 'xgb_reg_model'
n_features_to_select = 10

factor_select_path = factor_select_path + f'{strategy_name}/{model_name}/{version}/'

imptc_ranks = {}
def rank_to_dict(ranks, names, order=1):
    minmax = MinMaxScaler()
    ranks = minmax.fit_transform(order * np.array([ranks]).T).T[0]
    ranks = map(lambda x: round(x, 5), ranks)
    return dict(zip(names, ranks))

dp = DataPrepare()
samples = dp.get_samples()

date_config = dict(train_start_date=20160104,
                   train_end_date=20181231,
                   valid_start_date=20190102,
                   valid_end_date=20190930,
                   test_start_date=20191008,
                   test_end_date=20200630)
mf_inst = XGBRegModel(model_name=model_name,
                      date_config=date_config,
                      factor_filter_path=filter_factor_fpath,
                      factor_score_path=factor_score_fpath,
                      data_path=saturn_data_test_fpath,
                      label='label_pct')    # 设置

# drop掉要剔除的因子
factor_list = mf_inst.factor_list   # 输出全部的因子列表
drop_factor_list = list()
factor_list = list(set(factor_list).difference(set(drop_factor_list)))
mf_inst.factor_list = factor_list

X_train, y_train, _, _, _, _ = mf_inst.get_dateset()

class FactorSelection:
    def __init__(self, X_train, y_train):
        self.X_train = X_train
        self.y_train = y_train
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_train_scaled = pd.DataFrame(X_train_scaled, index=X_train.index, columns=X_train.columns)
        self.X_train_scaled = X_train_scaled
        self.imptc_ranks = dict()

    def calc_lr_imptc(self):
        # 线性回归看系数
        t1 = time.time()
        lr = LogisticRegression(penalty='l2')
        lr.fit(self.X_train_scaled, self.y_train > 0)
        self.imptc_ranks['LR'] = rank_to_dict(lr.coef_.reshape(-1), factor_list)
        print(f'逻辑回归lr计算耗时：{time.time() - t1}秒')

    def calc_ridge_imptc(self):
        # Ridge
        t1 = time.time()
        ridge = RidgeClassifier(alpha=7)
        _ = ridge.fit(self.X_train_scaled, self.y_train > 0)
        self.imptc_ranks['Ridge'] = rank_to_dict(np.abs(ridge.coef_.reshape(-1)), factor_list)
        print(f'ridge计算耗时：{time.time() - t1}秒')

    def calc_rlasso_imptc(self):
        # rLasso
        t1 = time.time()
        rlasso = RandomizedLogisticRegression()
        rlasso.fit(self.X_train_scaled, self.y_train > 0)
        self.imptc_ranks['rlasso'] = rank_to_dict(np.abs(rlasso.scores_), factor_list)
        print(f'稳定性rlasso计算耗时：{time.time() - t1}秒')

    def calc_xgb_imptc(self):
        # XGB importance
        t1 = time.time()
        xg_model = xgb.XGBRegressor()
        xg_model.set_params(**model_params[model_name])
        rfe = RFE(xg_model, n_features_to_select=n_features_to_select, verbose=True)
        rfe.fit(self.X_train, self.y_train)
        self.imptc_ranks['rfe_xgb'] = rank_to_dict(list(map(float, rfe.ranking_)), factor_list, order=-1)
        print(f'rfe_xgb计算耗时：{time.time() - t1}秒')

    def calc_gbr_imptc(self):
        # GBR importance
        t1 = time.time()
        gbdt_model = GradientBoostingRegressor()
        gbdt_model.fit(X_train, y_train)
        rfe = RFE(gbdt_model, n_features_to_select=n_features_to_select)
        rfe.fit(self.X_train, self.y_train)
        self.imptc_ranks['rfe_gbdt'] = rank_to_dict(list(map(float, rfe.ranking_)), factor_list, order=-1)
        print(f'rfe_gbdt计算耗时：{time.time() - t1}秒')

    def calc_rf_imptc(self):
        # RF importance
        t1 = time.time()
        rf = RandomForestRegressor()
        rf.fit(self.X_train, self.y_train)
        self.imptc_ranks['rf'] = rank_to_dict(rf.feature_importances_, factor_list)
        print(f'随机森林模型rf计算耗时：{time.time() - t1}秒')

    def calc_corr_imptc(self):
        # orr相关系数
        t1 = time.time()
        f, pval  = f_regression(self.X_train, self.y_train)
        self.imptc_ranks['corr'] = rank_to_dict(abs(f), factor_list)
        print(f'相关系数corr计算耗时：{time.time() - t1}秒')

    def calc_mic_imptc(self):
        # mutual_info_regression互信息
        t1 = time.time()
        mine = MINE()
        mic_scores = list()
        for col in self.X_train_scaled.columns.tolist():
            mine.compute_score(self.X_train_scaled.loc[:,col], y_train.values.reshape(-1))
            m = mine.mic()
            mic_scores.append(m)
        self.imptc_ranks['MIC'] = rank_to_dict(mic_scores, factor_list)
        print(f'互信息mic计算耗时：{time.time() - t1}秒')

    def calc_xgb_shap_imptc(self):
        t1 = time.time()
        xg_model = xgb.XGBRegressor()
        best_param = model_params[model_name].copy()
        best_param.update({'tree_method': 'hist'})
        xg_model.set_params(**best_param)
        xg_model.fit(self.X_train, self.y_train)
        explainer = shap.TreeExplainer(xg_model)
        shap_values = explainer.shap_values(X_train)
        shape_abs = abs(shap_values).mean(axis=0)
        self.imptc_ranks['shap_value'] = rank_to_dict(shape_abs, factor_list)
        print(f'shap_value计算耗时：{time.time() - t1}秒')

    @staticmethod
    def get_cond_data(data, bound, symbol='>'):
        if symbol is '>':
            factor_list = data[data >= bound].index.tolist()
        elif symbol is '<':
            factor_list = data[data <= bound].index.tolist()
        else:
            factor_list = data.index.tolist()
        return factor_list

    def launch(self):
        # self.calc_lr_imptc()    # LR
        # self.calc_ridge_imptc() # Ridge
        # self.calc_rlasso_imptc()    # rlasso
        self.calc_xgb_imptc()   # rfe_xgb
        # self.calc_gbr_imptc()   # rfe_gbdt
        # self.calc_rf_imptc() # rf
        # self.calc_corr_imptc()  # corr
        self.calc_xgb_shap_imptc()  # shap_value

        return self.imptc_ranks

    def filter(self, filter_conds):
        imptc_ranks_df = pd.DataFrame(self.imptc_ranks)
        filter_conds_str = '&'.join(filter_conds)
        imptc_ranks_df = imptc_ranks_df.query(filter_conds_str)
        return imptc_ranks_df.index.tolist()

    def filter_pct(self, filter_pct_conds):
        imptc_ranks_df = pd.DataFrame(self.imptc_ranks)
        _select = set(self.X_train.columns)
        for cond in filter_pct_conds:
            filter_method, operator, pct_threshold = cond.split(' ')
            filter_threshold = imptc_ranks_df[filter_method].quantile(q=float(pct_threshold))
            _tmp_select = imptc_ranks_df.query(f'{filter_method} {operator} {filter_threshold}').index.tolist()
            _select = _select.intersection(set(_tmp_select))
        return list(_select)


if __name__ == '__main__':
    fs = FactorSelection(X_train=X_train, y_train=y_train)
    if os.path.exists(factor_select_path + 'factor_selected.xlsx'):
        imptc_ranks_df = pd.read_excel(factor_select_path + 'factor_selected.xlsx', index_col=0)
        fs.imptc_ranks = imptc_ranks_df.to_dict()
    else:
        imptc_ranks = fs.launch()
        imptc_ranks_df = pd.DataFrame(imptc_ranks)
        FileUtil.save_df2xls(imptc_ranks_df, factor_select_path, 'factor_selected.xlsx')

    # TODO: 对特征选择矩阵进行选择，输出符合条件的特征
    # filter_conds = [
    #     # 'LR <= 0.5',
    #     # 'Ridge >= 0.8',
    #     # 'rlasso >= 0.7',
    #     'rfe_xgb >= 0.2',
    #     # 'rfe_gbdt >= 0.4',
    #     # 'rf >= 0.5',
    #     # 'corr >= 0.8',
    #     'shap_value >= 0.7'
    # ]
    # factor_list = fs.filter(filter_conds)

    filter_pct_conds = [
        'rfe_xgb >= 0.5',
        'shap_value >= 0.3'
    ]
    factor_list= fs.filter_pct(filter_pct_conds)
    FileUtil.save_list2pkl(factor_list, factor_select_path, 'factor_selected.pkl')