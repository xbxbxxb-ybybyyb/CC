import numpy as np
import pandas as pd
# 每日计算ins增长率，取20日平均
'''
每日IC的均值： -0.003478032180605223
2021IC的均值： -0.003766892515701975
2022IC的均值： -0.002858625555832925
2023IC的均值： -0.0038386807858829886
'''
factor_name = 'factor_qyh_heat_20231206_2'
def factor_qyh_heat_20231206_2(df_ori):
    df_ori['ins_delta'] = df_ori['ins'] / df_ori['ins'].unstack().shift(1).stack() - 1
    df_ori[factor_name] = df_ori['ins_delta'].unstack().rolling(20,1).mean().stack()
    return df_ori[[factor_name]]