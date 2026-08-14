import numpy as np
import pandas as pd
# 每日计算ins增长率，取20日增长率的标准差
'''
每日IC的均值： -0.03534796305254036
2021IC的均值： -0.023186345953328507
2022IC的均值： -0.0383232167072812
2023IC的均值： -0.04546226880213863
'''
factor_name = 'factor_qyh_heat_20231206_8'
def factor_qyh_heat_20231206_8(df_ori):
    df_ori['ins_delta'] = df_ori['ins'] / df_ori['ins'].unstack().shift(1).stack() - 1
    df_ori[factor_name] = df_ori['ins_delta'].unstack().rolling(20,1).std().stack()
    return df_ori[[factor_name]]