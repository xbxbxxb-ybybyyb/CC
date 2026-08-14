# coding: utf-8
# Author：fengchi863
"""
本文件用于准备数据，包括获取数据等
"""

from Zeus.Saturn.v3_0_7.path_conf import saturn_data_test_fpath
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler

class DataPrepare:
    def __init__(self):
        pass

    @staticmethod
    def get_samples(saturn_data_fpath=saturn_data_test_fpath):
        samples = pd.read_pickle(saturn_data_fpath)
        X = samples[filter(lambda x: x.find('label'), samples.columns.tolist())]

        # nan_flag = X.isnull().any()
        # has_nan_factor_list = nan_flag[nan_flag].index.tolist()

        # 这里做一个统计，以及输出有空值的因子
        # print('原样本中包含空值的因子有:', ','.join(has_nan_factor_list))
        # print('*' * 30)

        # 这里不去空，在后面再去空值
        X = X.dropna(how='any', axis=0)     # 去掉包含nan的行
        samples = samples.loc[X.index]
        return samples

    def standard_scale(self, factor_list):
        pass