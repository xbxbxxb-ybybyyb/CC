import numpy as np
import pandas as pd
# 每日计算ind增长率，取5日增长率的标准差（线性加权）
'''
每日IC的均值： -0.060686246727244396
2021IC的均值： -0.048528072055407545
2022IC的均值： -0.06743394272929336
2023IC的均值： -0.06666585764471294
'''
def linear_mean(df_ori, n):
    weight = [(n - i) / (n + 1) / n * 2 for i in range(0, n)]
    counter = 1
    df = pd.DataFrame()
    for x in weight:
        if counter == 1:
            df = df_ori * x
        else:
            df = df + df_ori.shift(counter - 1) * x
        counter = counter + 1
    return df
factor_name = 'factor_qyh_heat_20231206_15'
def factor_qyh_heat_20231206_15(df_ori):
    df_ori['ind_delta'] = df_ori['ind'] / df_ori['ind'].unstack().shift(1).stack() - 1
    df_ori['ind_mean'] = linear_mean(df_ori['ind_delta'].unstack(),5).stack()
    df_ori['ind_delmean_2'] = (df_ori['ind_delta'] - df_ori['ind_mean'])**2
    df_ori[factor_name] = linear_mean(df_ori['ind_delmean_2'].unstack(),5).stack()
    return df_ori[[factor_name]]