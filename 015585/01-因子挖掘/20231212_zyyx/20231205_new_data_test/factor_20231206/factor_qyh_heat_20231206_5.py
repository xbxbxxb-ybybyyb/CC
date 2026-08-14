import numpy as np
import pandas as pd
# 每日计算ind增长率，取20日增长率的标准差
'''
每日IC的均值： -0.05504936243925696
2021IC的均值： -0.04246890830619548
2022IC的均值： -0.0625672107234904
2023IC的均值： -0.06064995551414126
'''
factor_name = 'factor_qyh_heat_20231206_5'
def factor_qyh_heat_20231206_5(df_ori):
    df_ori['ind_delta'] = df_ori['ind'] / df_ori['ind'].unstack().shift(1).stack() - 1
    df_ori[factor_name] = df_ori['ind_delta'].unstack().rolling(20,1).std().stack()
    return df_ori[[factor_name]]