import numpy as np
import pandas as pd
# 每日计算ind增长率，取5日增长率的标准差
'''
每日IC的均值： -0.06035341432048795
2021IC的均值： -0.0482885607204887
2022IC的均值： -0.06710230845348697
2023IC的均值： -0.06622910230516665
'''
factor_name = 'factor_qyh_heat_20231206_14'
def factor_qyh_heat_20231206_14(df_ori):
    df_ori['ind_delta'] = df_ori['ind'] / df_ori['ind'].unstack().shift(1).stack() - 1
    df_ori[factor_name] = df_ori['ind_delta'].unstack().rolling(5,1).std().stack()
    return df_ori[[factor_name]]