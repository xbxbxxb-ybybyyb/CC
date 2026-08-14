import numpy as np
import pandas as pd
# 分别计算ins和ind的增长率，相减得到综合增长率，取综合增长率的20日均值
'''
每日IC的均值： 0.0012978290401444278
2021IC的均值： -0.0006490561863841534
2022IC的均值： 0.0029719322027286447
2023IC的均值： 0.0016053410071175693
'''
factor_name = 'factor_qyh_heat_20231206_10'
def factor_qyh_heat_20231206_10(df_ori):
    df_ori['ins_delta'] = df_ori['ins'] / df_ori['ins'].unstack().shift(1).stack() - 1
    df_ori['ind_delta'] = df_ori['ind'] / df_ori['ind'].unstack().shift(1).stack() - 1
    df_ori['delta'] = df_ori['ins_delta'] - df_ori['ind_delta']
    df_ori[factor_name] = df_ori['delta'].unstack().rolling(20,1).mean().stack()
    return df_ori[[factor_name]]