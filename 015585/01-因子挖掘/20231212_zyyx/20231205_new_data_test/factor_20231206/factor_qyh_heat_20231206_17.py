import numpy as np
import pandas as pd
# 散户增长率的5日最大值在全市场的相对排名 - 机构增长率的20日均值在全市场的相对排名
'''
每日IC的均值： -0.04718999618365005
2021IC的均值： -0.038137549697500474
2022IC的均值： -0.05402725598329147
2023IC的均值： -0.0496566370190397
'''
#ind-diff_nofilter_5_max_rank-ins-diff_nofilter_20_avg_rank-minus
factor_name = 'factor_qyh_heat_20231206_17'
def rank_(data_):
    data_r = (data_.unstack().rank(axis=1) / (~ data_.unstack().isnull()).values.sum(axis=1).reshape(-1, 1)).stack()
    return data_r
def factor_qyh_heat_20231206_17(df_ori):
    df_ori['ind_delta'] = df_ori['ind'] / df_ori['ind'].unstack().shift(1).stack() - 1
    df_ori['factor_ind'] = rank_(df_ori['ind_delta'].unstack().rolling(5,1).max().stack())
    df_ori['ins_delta'] = df_ori['ins'].unstack().diff().stack() / df_ori['ins'].unstack().max(axis=1)
    df_ori['factor_ins'] = rank_(df_ori['ins_delta'].unstack().rolling(20,1).mean().stack())
    df_ori[factor_name] = df_ori['factor_ind'] - df_ori['factor_ins']
    return df_ori[[factor_name]]