import numpy as np
import pandas as pd
# 分别计算ins和ind的增长率，相减得到综合增长率，取综合增长率的5日标准差
'''
每日IC的均值： -0.042566647106610254
2021IC的均值： -0.029327898837066362
2022IC的均值： -0.047187634454799066
2023IC的均值： -0.05206319412578442
'''
factor_name = 'factor_qyh_heat_20231206_11'
def factor_qyh_heat_20231206_11(df_ori):
    df_ori['ins_delta'] = df_ori['ins'] / df_ori['ins'].unstack().shift(1).stack() - 1
    df_ori['ind_delta'] = df_ori['ind'] / df_ori['ind'].unstack().shift(1).stack() - 1
    df_ori['delta'] = df_ori['ins_delta'] - df_ori['ind_delta']
    df_ori[factor_name] = df_ori['delta'].unstack().rolling(5,1).std().stack()
    return df_ori[[factor_name]]