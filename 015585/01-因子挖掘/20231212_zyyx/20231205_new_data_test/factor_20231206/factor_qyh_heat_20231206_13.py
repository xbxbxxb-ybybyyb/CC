import numpy as np
import pandas as pd
# 【原始逻辑】
# 1、ind和ins分别计算增长率
# 2、分别对增长率取22日线性加权
# 3、每日进行z_score
# 4、再相减
'''
每日IC的均值： 0.019215337616973405
2021IC的均值： 0.01611339455882654
2022IC的均值： 0.0229052660586723
2023IC的均值： 0.018585516260586722
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
factor_name = 'factor_qyh_heat_20231206_13'
def factor_qyh_heat_20231206_13(df_ori):
    df_ori['ins_delta'] = (df_ori['ins'] - df_ori['ins'].unstack().shift(1).stack()) / df_ori['ins'].unstack().quantile(0.99,axis=1)
    df_ori['ind_delta'] = df_ori['ind'] / df_ori['ind'].unstack().shift(1).stack() - 1
    df_ins_mean = linear_mean(df_ori['ins_delta'].unstack(),22)
    df_ind_mean = linear_mean(df_ori['ind_delta'].unstack(),22)
    df_ins = (df_ins_mean.sub(df_ins_mean.mean(axis=1),axis=0).divide(df_ins_mean.std(axis=1),axis=0)).stack()
    df_ind = (df_ind_mean.sub(df_ind_mean.mean(axis=1),axis=0).divide(df_ind_mean.std(axis=1),axis=0)).stack()
    df_ori[factor_name] = df_ins - df_ind
    df_ori[factor_name] = df_ind_mean
    return df_ori[[factor_name]]

'''
ins:
每日IC的均值： 0.0263244799496412
2021IC的均值： 0.020670217875526357
2022IC的均值： 0.03015549066993743
2023IC的均值： 0.028346566328366157
ind:
每日IC的均值： -0.029659347203635236
2021IC的均值： -0.024004049992273152
2022IC的均值： -0.03363254749109845
2023IC的均值： -0.03152687097193787
'''