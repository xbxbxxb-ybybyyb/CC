import numpy as np
import pandas as pd
# 分别计算ins和ind的增长率，相减得到综合增长率，取综合增长率的5日标准差
'''
每日IC的均值： -0.03953934217179795
2021IC的均值： -0.027794795275184307
2022IC的均值： -0.042590077576379844
2023IC的均值： -0.04911240519427897
'''
factor_name = 'factor_qyh_heat_20231206_12'
def factor_qyh_heat_20231206_12(df_ori):
    df_ori['ins_delta'] = df_ori['ins'] / df_ori['ins'].unstack().shift(1).stack() - 1
    df_ori['ind_delta'] = df_ori['ind'] / df_ori['ind'].unstack().shift(1).stack() - 1
    df_ori['delta'] = df_ori['ins_delta'] - df_ori['ind_delta']
    df_ori[factor_name] = df_ori['delta'].unstack().rolling(20,1).std().stack()
    return df_ori[[factor_name]]