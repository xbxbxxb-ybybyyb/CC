import numpy as np
import pandas as pd
# ind数量20日的变异系数
'''
每日IC的均值： -0.04946929940052447
2021IC的均值： -0.0410160157178173
2022IC的均值： -0.05446281497810487
2023IC的均值： -0.05329607390334525
'''
factor_name = 'factor_qyh_heat_20231206_7'
def factor_qyh_heat_20231206_7(df_ori):
    df_ori[factor_name] = df_ori['ind'].unstack().rolling(20,1).std().stack() / (df_ori['ind'].unstack().rolling(20,1).mean().stack() +1e-2)
    return df_ori[[factor_name]]