import numpy as np
import pandas as pd
# 每日计算ind增长率，取5日平均
'''
每日IC的均值： -0.022747966815134184
2021IC的均值： -0.02136128645615296
2022IC的均值： -0.025293173753044844
2023IC的均值： -0.021485628571957956
'''
factor_name = 'factor_qyh_heat_20231206_3'
def factor_qyh_heat_20231206_3(df_ori):
    df_ori['ind_delta'] = df_ori['ind'] / df_ori['ind'].unstack().shift(1).stack() - 1
    df_ori[factor_name] = df_ori['ind_delta'].unstack().rolling(5,1).mean().stack()
    return df_ori[[factor_name]]