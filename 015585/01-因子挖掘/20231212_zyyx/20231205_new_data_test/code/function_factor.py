import numpy as np
import pandas as pd
# diff or not
def f_pro_diff(df_ori,type):
    if type == 'ind':
        df_ori['factor'] = df_ori[type].unstack().diff().stack() / df_ori[type].unstack().shift(1).stack()
    if type == 'ins':
        df_ori['factor'] = df_ori[type].unstack().diff().stack() / df_ori[type].unstack().max(axis=1)
    return df_ori
def f_pro_nodiff(df_ori,type):
    df_ori['factor'] = df_ori[type]
    return df_ori
# rolling的筛选方式
def f_roll_filter_nofilter(df_ori, type):
    return df_ori
def f_roll_filter_up1(df_ori, type): # 只取增加，其他为nan
    df_ori['up'] = np.sign(df_ori[type].unstack().diff().stack())
    df_ori['up'] = df_ori['up'].apply(lambda x : 1 if x >= 0.5 else np.nan)
    df_ori['factor'] = df_ori['factor'] * df_ori['up']
    return df_ori
def f_roll_filter_down1(df_ori, type): # 只取减少，其他为nan
    df_ori['down'] = np.sign(df_ori[type].unstack().diff().stack())
    df_ori['down'] = df_ori['down'].apply(lambda x : -1 if x <= -0.5 else np.nan)
    df_ori['factor'] = df_ori['factor'] * df_ori['down']
    return df_ori
# rolling后计算
def f_calc_nocalc(factor_series):
    return
def f_calc_max(factor_series):
    return factor_series[~np.isnan(factor_series)].max()
def f_calc_min(factor_series):
    return factor_series[~np.isnan(factor_series)].min()
def f_calc_med(factor_series):
    return np.median(factor_series[~np.isnan(factor_series)])
def f_calc_avg(factor_series):
    return factor_series[~np.isnan(factor_series)].mean()
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

def f_calc_cv(factor_series):
    if  abs(f_calc_avg(factor_series)) > 0:
        return np.std(factor_series[~np.isnan(factor_series)],ddof=1) / f_calc_avg(factor_series)
    else:
        return np.nan
def f_calc_sum(factor_series):
    return factor_series[~np.isnan(factor_series)].sum()
def f_calc_cct(factor_series):
    if abs(f_calc_sum(factor_series)) > 0:
        return f_calc_sum(factor_series**2) / (f_calc_sum(factor_series)**2)
    else:
        return np.nan
def f_calc_skew(factor_series):
    factor_series = factor_series[~np.isnan(factor_series)]
    mean = factor_series.mean()
    std = factor_series.std(ddof=1)
    n = len(factor_series)
    if n > 3:
        skew = sum(((factor_series-mean)/std)**3) * n / (n-1) / (n-2)
    else:
        skew = np.nan
    return skew
def f_calc_kurt(factor_series):
    factor_series = factor_series[~np.isnan(factor_series)]
    mean = factor_series.mean()
    std = factor_series.std(ddof=1)
    n = len(factor_series)
    if n < 4:
        return np.nan
    else:
        kurt = sum(((factor_series-mean)/std)**4)
        kurt = kurt * n * (n+1) / (n-1) / (n-2) / (n-3) - 3*(n-1)*(n-1)/(n-2)/(n-3)
        return kurt
def f_calc_change(factor_series):
    return factor_series[-1] - factor_series[0]
def f_calc_m2m(factor_series):
    factor_series = factor_series[~np.isnan(factor_series)]
    return factor_series.max() / factor_series.mean() if factor_series.mean()>0 else np.nan
def f_calc_pos(factor_series):
    factor_series = factor_series[~np.isnan(factor_series)]
    return (factor_series[-1] - factor_series.min()) / \
           (factor_series.max() - factor_series.min() + 1e-8)
def f_calc_std(factor_series):
    factor_series = factor_series[~np.isnan(factor_series)]
    return np.std(factor_series,ddof=1)
# 标准化函数:rank / std / no
def rank_(data_):
    data_r = (data_.unstack().rank(axis=1) / (~ data_.unstack().isnull()).values.sum(axis=1).reshape(-1, 1)).stack()
    return data_r
def f_std_rank(df):
    df['factor'] = rank_(df['factor'])
    return df[['factor']]
def f_std_zscore(df):
    df['factor'] = (df['factor'] - df['factor'].unstack().mean(axis=1)) / df['factor'].unstack().std(axis=1)
    return df[['factor']]
def f_std_nostd(df):
    return df[['factor']]
# combo函数：加减乘除
def f_combo_add(df):
    return pd.DataFrame(df['factor_ind'] + df['factor_ins'])
def f_combo_minus(df):
    return pd.DataFrame(df['factor_ind'] - df['factor_ins'])
def f_combo_multi(df):
    return pd.DataFrame(df['factor_ind'] * df['factor_ins'])
def f_combo_div(df):
    return pd.DataFrame(df['factor_ind'] / df['factor_ins'])
#
import pickle
def save_pickle(result_dic, save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(result_dic, input, protocol=pickle.HIGHEST_PROTOCOL)