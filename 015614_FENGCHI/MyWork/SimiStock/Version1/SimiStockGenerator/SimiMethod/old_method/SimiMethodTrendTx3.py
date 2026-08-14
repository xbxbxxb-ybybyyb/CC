# coding: utf-8
# Author：fengchi863
# Date ：2022/3/11 14:31

"""
第三个版本，采用V3
V0是不带有风格权重的信息
网格调参多种参数下的回测结果
"""

from SimiStockGenerator.SimiMethodBase.SimiMethodBase import SimiMethodBase
from sklearn.preprocessing import MinMaxScaler, Imputer
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
import pandas as pd
from itertools import product

"""皮尔逊相似度、规模、波动、动量、质量"""
weight_dict = {'v1': [0.6, 0.4, 0, 0, 0],
               'v2': [0.8, 0.2, 0, 0, 0],
               'v3': [0.6, 0.2, 0.2, 0, 0],
               'v4': [0.6, 0.2, 0.1, 0.1, 0],
               'v5': [0.6, 0.1, 0.1, 0.1, 0.1],
               'v6': [0.4, 0.2, 0.2, 0.1, 0.1],
               'v7': [0.5, 0.3, 0.2, 0.1, 0.1],
               'v8': [0, 0.1, 0.1, 0.1, 0.7]}


class SimiStyleMethod(SimiMethodBase):
    def __init__(self, start_date=20180101, end_date=20211231, concept='SW1', pre_days_num=120, hedge_max_num=12,
                 corr_threshold=0.8, weight_kind='v1', method_name=None):
        super().__init__(start_date, end_date, concept=concept)
        corr = pd.read_pickle(factor_path + 'pct_pearson_corr_120.pkl')
        roa = pd.read_pickle(factor_path + 'ROA.pkl')
        rstr = pd.read_pickle(factor_path + 'RSTR.pkl')
        dastd = pd.read_pickle(factor_path + 'DASTD.pkl')
        lncap = pd.read_pickle(factor_path + 'LNCAP.pkl')

        self.method_name = method_name
        self.pre_days_num = pre_days_num
        self.corr = self.min_max_transfer(corr)
        self.lncap = self.min_max_transfer(lncap)
        self.dastd = self.min_max_transfer(dastd)
        self.rstr = self.min_max_transfer(rstr)
        self.roa = self.min_max_transfer(roa)

        self.hedge_max_num = hedge_max_num
        self.corr_threshold = corr_threshold
        self.weight_kind = weight_kind

    def min_max_transfer(self, df: pd.DataFrame):
        tmp_df = df.copy()
        scaler = MinMaxScaler()
        im = Imputer(missing_values='NaN', strategy='mean', axis=1)
        tmp_df = im.fit_transform(tmp_df)
        ret = scaler.fit_transform(tmp_df.T)
        ret = ret.T
        ret = pd.DataFrame(ret, columns=df.columns, index=df.index)
        return ret

    def simi_strategy(self, stk_id, trade_date, concept_list):
        weight_list = weight_dict[self.weight_kind]
        ret_df = self.corr.loc[(trade_date, stk_id)] * weight_list[0] - \
            self.lncap.loc[(trade_date, stk_id)] * weight_list[1] - \
            self.dastd.loc[(trade_date, stk_id)] * weight_list[2] - \
            self.rstr.loc[(trade_date, stk_id)] * weight_list[3] - \
            self.roa.loc[(trade_date, stk_id)] * weight_list[4]

        ret_df = ret_df[concept_list].sort_values(ascending=False)
        tmp_list1 = ret_df.index.tolist()[:self.hedge_max_num]
        s_corr = self.corr.loc[(trade_date, stk_id)][concept_list]
        tmp_list2 = s_corr[s_corr > self.corr_threshold].index.tolist()
        ret_list = [x for x in tmp_list1 for y in tmp_list2 if x == y]
        return ret_list, [1] * len(ret_list), ret_df[ret_list].tolist()


if __name__ == '__main__':
    param_dict = {'method_name': ['叠加风格'],
                  'concept': ['SW1'],
                  'pre_days_num': [120],
                  'hedge_max_num': [5, 8, 11, 14, 17],
                  'corr_threshold': [0.7],
                  'weight_kind': ['v3']}
    param_list = list(product(param_dict['method_name'],
                              param_dict['concept'],
                              param_dict['pre_days_num'],
                              param_dict['hedge_max_num'],
                              param_dict['corr_threshold'],
                              param_dict['weight_kind']))
    for param in param_list:
        method_name = param[0]
        concept = param[1]
        pre_days_num = param[2]
        hedge_max_num = param[3]
        corr_threshold = param[4]
        weight_kind = param[5]
        smt1 = SimiStyleMethod(start_date=20180101, end_date=20200630, concept=concept, pre_days_num=pre_days_num,
                               hedge_max_num=hedge_max_num, corr_threshold=corr_threshold, weight_kind=weight_kind,
                               method_name=method_name)
        result = smt1.get_hedge_list(mode='multi', kernal_num=24)
        save_name = f'{method_name}_{hedge_max_num}_{corr_threshold}_{weight_kind}_txresult.pkl'
        util.save_list2pkl(result, hedge_path, save_name)