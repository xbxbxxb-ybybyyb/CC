import numpy as np
import pandas as pd
# 每日计算ins增长率，取5日平均
'''
每日IC的均值： 0.011423686469701128
2021IC的均值： 0.011545773137579351
2022IC的均值： 0.007492629973951392
2023IC的均值： 0.015594042178646926
'''
factor_name = 'factor_qyh_heat_20231206_1'
def factor_qyh_heat_20231206_1(df_ori):
    df_ori['ins_delta'] = df_ori['ins'] / df_ori['ins'].unstack().shift(1).stack() - 1
    df_ori[factor_name] = df_ori['ins_delta'].unstack().rolling(5,1).mean().stack()
    return df_ori[[factor_name]]