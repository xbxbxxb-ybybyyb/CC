import numpy as np
import pandas as pd
# 每日计算ind增长率，取20日平均
'''
每日IC的均值： -0.026178223930613115
2021IC的均值： -0.019246840573882783
2022IC的均值： -0.029870925752435582
2023IC的均值： -0.029756017210271248
'''
factor_name = 'factor_qyh_heat_20231206_4'
def factor_qyh_heat_20231206_4(df_ori):
    df_ori['ind_delta'] = df_ori['ind'] / df_ori['ind'].unstack().shift(1).stack() - 1
    df_ori[factor_name] = df_ori['ind_delta'].unstack().rolling(20,1).mean().stack()
    return df_ori[[factor_name]]