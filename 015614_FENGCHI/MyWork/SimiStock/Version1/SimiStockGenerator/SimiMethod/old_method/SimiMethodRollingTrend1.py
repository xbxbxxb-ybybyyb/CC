# coding: utf-8
# Author：fengchi863
# Date ：2022/4/8 0:25

"""
滚动样例，继承自SimiMethodRollingBase
其中随机取行业中的一部分股票
提供给陶鑫测试用
"""

from SimiStockGenerator.SimiMethodBase.SimiMethodRollingBase import SimiMethodRollingBase
from sklearn.preprocessing import MinMaxScaler, Imputer
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
import numpy as np
import pandas as pd
from itertools import product

"""皮尔逊相似度、规模、波动、动量、质量"""
weight_dict = {'v0': [1, 0, 0],
               'v1': [0.6, 0.4, 0],
               'v2': [0.8, 0.2, 0],
               'v3': [0.6, 0.2, 0.2]}


class SimiMethodRollingTrend1(SimiMethodRollingBase):
    def __init__(self, start_date=20180101, end_date=20211231, concept='SW1', pre_days_num=252, hedge_max_num=12,
                 corr_threshold=0.8, weight_kind='v1', method_name=None, discount=95):
        super().__init__(start_date, end_date, concept=concept, discount=discount)
        corr = pd.read_pickle(factor_path + 'pct_pearson_corr.pkl')
        corr2 = pd.read_pickle(factor_path + 'pct_pearson_corr.pkl')
        dastd = pd.read_pickle(factor_path + 'DASTD.pkl')
        lncap = pd.read_pickle(factor_path + 'LNCAP.pkl')

        self.method_name = method_name
        self.pre_days_num = pre_days_num
        self.corr2 = corr2
        self.corr = self.min_max_transfer(corr)
        self.lncap = self.min_max_transfer(lncap)
        self.dastd = self.min_max_transfer(dastd)

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

    def simi_strategy(self, stk_id, date_tuple_list):
        hedge_list = list()
        for date_tuple in date_tuple_list:
            calc_date, start_date, end_date, train_start_date, end_start_date = date_tuple
            concept_list = self.get_concept_list(stk_id, calc_date)
            hedge_num = min(np.random.randint(0, 5), len(concept_list))
            append_dict = {'calc_date': calc_date,
                           'start_date': start_date,
                           'end_date': end_date,
                           'hedge_list': concept_list[:hedge_num]}
            hedge_list.append(append_dict)
        return hedge_list


if __name__ == '__main__':
    param_dict = {'method_name': ['滚动'],
                  'concept': ['SW1'],
                  'pre_days_num': [120],
                  'hedge_max_num': [14],
                  'corr_threshold': [0.8],
                  'weight_kind': ['v3'],
                  'discount': [95]}
    param_list = list(product(param_dict['method_name'],
                              param_dict['concept'],
                              param_dict['pre_days_num'],
                              param_dict['hedge_max_num'],
                              param_dict['corr_threshold'],
                              param_dict['weight_kind'],
                              param_dict['discount']))
    for param in param_list:
        method_name = param[0]
        concept = param[1]
        pre_days_num = param[2]
        hedge_max_num = param[3]
        corr_threshold = param[4]
        weight_kind = param[5]
        discount = param[6]
        smt1 = SimiMethodRollingTrend1(start_date=20200620, end_date=20200630, concept=concept, pre_days_num=pre_days_num,
                               hedge_max_num=hedge_max_num, corr_threshold=corr_threshold, weight_kind=weight_kind,
                               method_name=method_name, discount=discount)
        result = smt1.get_hedge_list(mode='serial', kernal_num=24)
#        result = smt1.get_hedge_list(mode='multi', kernal_num=24)
        save_name = f'{method_name}_{hedge_max_num}_{corr_threshold}_{weight_kind}_{discount}_20180101_20200630_result.pkl'
        util.save_list2pkl(result, hedge_path, save_name)