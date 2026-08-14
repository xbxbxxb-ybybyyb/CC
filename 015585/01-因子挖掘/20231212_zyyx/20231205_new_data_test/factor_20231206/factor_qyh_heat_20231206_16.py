import numpy as np
import pandas as pd
# 每日计算ind增长率，取5日增长率的max / mean
'''
每日IC的均值： -0.016924909732154145
2021IC的均值： -0.016391411256127513
2022IC的均值： -0.017541128876917236
2023IC的均值： -0.016836742748632835
'''
factor_name = 'factor_qyh_heat_20231206_16'
def factor_qyh_heat_20231206_16(df_ori):
    df_ori['ind_delta'] = df_ori['ind'] / df_ori['ind'].unstack().shift(1).stack() - 1
    df_ori[factor_name] = df_ori['ind_delta'].unstack().rolling(5,1).max().stack() / df_ori['ind_delta'].unstack().rolling(5,1).mean().stack()
    return df_ori[[factor_name]]