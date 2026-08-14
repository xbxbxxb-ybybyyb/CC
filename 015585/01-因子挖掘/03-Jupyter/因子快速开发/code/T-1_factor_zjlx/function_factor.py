import numpy as np
import pandas as pd
# 因子属性
def f_pro_bjg(df_ori): # buy jg
    df_ori['factor'] = df_ori['BUY_VALUE_EXLARGE_ORDER']
    return df_ori
def f_pro_bjg2amt(df_ori): # buy jg
    df_ori['factor'] = df_ori['BUY_VALUE_EXLARGE_ORDER'] / df_ori['amt']
    return df_ori
def f_pro_bjg2mv(df_ori): # buy jg
    df_ori['factor'] = df_ori['BUY_VALUE_EXLARGE_ORDER'] / df_ori['mkt_cap_ard']
    return df_ori
def f_pro_bjgratio(df_ori): #
    df_ori['factor'] = df_ori['BUY_VALUE_EXLARGE_ORDER'] / (df_ori['BUY_VALUE_EXLARGE_ORDER'] + df_ori['BUY_VALUE_LARGE_ORDER'] + df_ori['BUY_VALUE_MED_ORDER'] + df_ori['BUY_VALUE_SMALL_ORDER'])
    return df_ori
def f_pro_bjgdhratio(df_ori): #
    df_ori['factor'] = (df_ori['BUY_VALUE_EXLARGE_ORDER'] + df_ori['BUY_VALUE_LARGE_ORDER']) / (df_ori['BUY_VALUE_EXLARGE_ORDER'] + df_ori['BUY_VALUE_LARGE_ORDER'] + df_ori['BUY_VALUE_MED_ORDER'] + df_ori['BUY_VALUE_SMALL_ORDER'])
    return df_ori
def f_pro_bshratio(df_ori): #
    df_ori['factor'] = (df_ori['BUY_VALUE_SMALL_ORDER']) / (df_ori['BUY_VALUE_EXLARGE_ORDER'] + df_ori['BUY_VALUE_LARGE_ORDER'] + df_ori['BUY_VALUE_MED_ORDER'] + df_ori['BUY_VALUE_SMALL_ORDER'])
    return df_ori
def f_pro_sjg(df_ori): # SELL jg
    df_ori['factor'] = df_ori['SELL_VALUE_EXLARGE_ORDER']
    return df_ori
def f_pro_sjgratio(df_ori): #
    df_ori['factor'] = df_ori['SELL_VALUE_EXLARGE_ORDER'] / (df_ori['SELL_VALUE_EXLARGE_ORDER'] + df_ori['SELL_VALUE_LARGE_ORDER'] + df_ori['SELL_VALUE_MED_ORDER'] + df_ori['SELL_VALUE_SMALL_ORDER'])
    return df_ori
def f_pro_sjgdhratio(df_ori): #
    df_ori['factor'] = (df_ori['SELL_VALUE_EXLARGE_ORDER'] + df_ori['SELL_VALUE_LARGE_ORDER']) / (df_ori['SELL_VALUE_EXLARGE_ORDER'] + df_ori['SELL_VALUE_LARGE_ORDER'] + df_ori['SELL_VALUE_MED_ORDER'] + df_ori['SELL_VALUE_SMALL_ORDER'])
    return df_ori
def f_pro_sshratio(df_ori): #
    df_ori['factor'] = (df_ori['SELL_VALUE_SMALL_ORDER']) / (df_ori['SELL_VALUE_EXLARGE_ORDER'] + df_ori['SELL_VALUE_LARGE_ORDER'] + df_ori['SELL_VALUE_MED_ORDER'] + df_ori['SELL_VALUE_SMALL_ORDER'])
    return df_ori
def f_pro_tradescount(df_ori): #
    df_ori['factor'] = (df_ori['TRADES_COUNT'])
    return df_ori
# 笔数
def f_pro_btradesjg(df_ori): # buy jg
    df_ori['factor'] = df_ori['BUY_TRADES_EXLARGE_ORDER']
    return df_ori
def f_pro_btradesjgratio(df_ori): #
    df_ori['factor'] = df_ori['BUY_TRADES_EXLARGE_ORDER'] / (df_ori['BUY_TRADES_EXLARGE_ORDER'] + df_ori['BUY_TRADES_LARGE_ORDER'] + df_ori['BUY_TRADES_MED_ORDER'] + df_ori['BUY_TRADES_SMALL_ORDER'])
    return df_ori
def f_pro_btradesjgdhratio(df_ori): #
    df_ori['factor'] = (df_ori['BUY_TRADES_EXLARGE_ORDER'] + df_ori['BUY_TRADES_LARGE_ORDER']) / (df_ori['BUY_TRADES_EXLARGE_ORDER'] + df_ori['BUY_TRADES_LARGE_ORDER'] + df_ori['BUY_TRADES_MED_ORDER'] + df_ori['BUY_TRADES_SMALL_ORDER'])
    return df_ori
def f_pro_btradesshratio(df_ori): #
    df_ori['factor'] = (df_ori['BUY_TRADES_SMALL_ORDER']) / (df_ori['BUY_TRADES_EXLARGE_ORDER'] + df_ori['BUY_TRADES_LARGE_ORDER'] + df_ori['BUY_TRADES_MED_ORDER'] + df_ori['BUY_TRADES_SMALL_ORDER'])
    return df_ori
def f_pro_stradesjg(df_ori): # SELL jg
    df_ori['factor'] = df_ori['SELL_TRADES_EXLARGE_ORDER']
    return df_ori
def f_pro_stradesjgratio(df_ori): #
    df_ori['factor'] = df_ori['SELL_TRADES_EXLARGE_ORDER'] / (df_ori['SELL_TRADES_EXLARGE_ORDER'] + df_ori['SELL_TRADES_LARGE_ORDER'] + df_ori['SELL_TRADES_MED_ORDER'] + df_ori['SELL_TRADES_SMALL_ORDER'])
    return df_ori
def f_pro_stradesjgdhratio(df_ori): #
    df_ori['factor'] = (df_ori['SELL_TRADES_EXLARGE_ORDER'] + df_ori['SELL_TRADES_LARGE_ORDER']) / (df_ori['SELL_TRADES_EXLARGE_ORDER'] + df_ori['SELL_TRADES_LARGE_ORDER'] + df_ori['SELL_TRADES_MED_ORDER'] + df_ori['SELL_TRADES_SMALL_ORDER'])
    return df_ori
def f_pro_stradesshratio(df_ori): #
    df_ori['factor'] = (df_ori['SELL_TRADES_SMALL_ORDER']) / (df_ori['SELL_TRADES_EXLARGE_ORDER'] + df_ori['SELL_TRADES_LARGE_ORDER'] + df_ori['SELL_TRADES_MED_ORDER'] + df_ori['SELL_TRADES_SMALL_ORDER'])
    return df_ori
# 金额差自身对比
def f_pro_valuesh(df_ori): #
    df_ori['factor'] = df_ori['VALUE_DIFF_SMALL_TRADER']
    return df_ori
def f_pro_valuesh2amt(df_ori): #
    df_ori['factor'] = df_ori['VALUE_DIFF_SMALL_TRADER'] / df_ori['amt']
    return df_ori
def f_pro_valuesh2mv(df_ori): #
    df_ori['factor'] = df_ori['VALUE_DIFF_SMALL_TRADER'] / df_ori['mkt_cap_ard']
    return df_ori
def f_pro_valueshact(df_ori): #
    df_ori['factor'] = df_ori['VALUE_DIFF_SMALL_TRADER_ACT']
    return df_ori
def f_pro_valueshact2amt(df_ori): #
    df_ori['factor'] = df_ori['VALUE_DIFF_SMALL_TRADER_ACT'] / df_ori['amt']
    return df_ori
def f_pro_valueshact2mv(df_ori): #
    df_ori['factor'] = df_ori['VALUE_DIFF_SMALL_TRADER_ACT'] / df_ori['mkt_cap_ard']
    return df_ori

def f_pro_valuejg(df_ori): #
    df_ori['factor'] = df_ori['VALUE_DIFF_INSTITUTE']
    return df_ori
def f_pro_valuejg2amt(df_ori): #
    df_ori['factor'] = df_ori['VALUE_DIFF_INSTITUTE'] / df_ori['amt']
    return df_ori
def f_pro_valuejg2mv(df_ori): #
    df_ori['factor'] = df_ori['VALUE_DIFF_INSTITUTE'] / df_ori['mkt_cap_ard']
    return df_ori
def f_pro_valuejgact(df_ori): #
    df_ori['factor'] = df_ori['VALUE_DIFF_INSTITUTE_ACT']
    return df_ori
def f_pro_valuejgact2amt(df_ori): #
    df_ori['factor'] = df_ori['VALUE_DIFF_INSTITUTE_ACT'] / df_ori['amt']
    return df_ori
def f_pro_valuejgact2mv(df_ori): #
    df_ori['factor'] = df_ori['VALUE_DIFF_INSTITUTE_ACT'] / df_ori['mkt_cap_ard']
    return df_ori
def f_pro_valuesh2jg(df_ori): #
    df_ori['factor'] = df_ori['VALUE_DIFF_SMALL_TRADER'] / df_ori['VALUE_DIFF_INSTITUTE']
    df_ori['factor'] = df_ori['factor'].apply(lambda x : 1e5 if x > 1e5 else -1e5 if x < -1e5 else x)
    return df_ori
def f_pro_valuesh2jgact(df_ori): #
    df_ori['factor'] = df_ori['VALUE_DIFF_SMALL_TRADER_ACT'] / df_ori['VALUE_DIFF_INSTITUTE_ACT']
    df_ori['factor'] = df_ori['factor'].apply(lambda x : 1e5 if x > 1e5 else -1e5 if x < -1e5 else x)
    return df_ori
#
def f_pro_valuekplr(df_ori): #
    df_ori['factor'] = df_ori['S_MFD_INFLOW_OPEN'] / df_ori['mkt_cap_ard']
    return df_ori
def f_pro_valuekplr2mv(df_ori): #
    df_ori['factor'] = df_ori['S_MFD_INFLOW_OPEN'] / df_ori['mkt_cap_ard']
    return df_ori
def f_pro_valuekplr2amt(df_ori): #
    df_ori['factor'] = df_ori['S_MFD_INFLOW_OPEN'] / df_ori['amt']
    return df_ori
def f_pro_ratiokplr(df_ori): #
    df_ori['factor'] = df_ori['OPEN_NET_INFLOW_RATE_VALUE']
    return df_ori
def f_pro_zjlxraio(df_ori): #
    df_ori['factor'] = df_ori['MONEYFLOW_PCT_VOLUME']
    return df_ori
def f_pro_ddjlrraio(df_ori): #
    df_ori['factor'] = df_ori['NET_INFLOW_RATE_VOLUME_L']
    return df_ori
# act
def f_pro_bjgact(df_ori): # buy jg
    df_ori['factor'] = df_ori['BUY_VALUE_EXLARGE_ORDER_ACT']
    return df_ori
def f_pro_bjgact2amt(df_ori): # buy jg
    df_ori['factor'] = df_ori['BUY_VALUE_EXLARGE_ORDER_ACT'] / df_ori['amt']
    return df_ori
def f_pro_bjgact2mv(df_ori): # buy jg
    df_ori['factor'] = df_ori['BUY_VALUE_EXLARGE_ORDER_ACT'] / df_ori['mkt_cap_ard']
    return df_ori
def f_pro_bjgactratio(df_ori): #
    df_ori['factor'] = df_ori['BUY_VALUE_EXLARGE_ORDER_ACT'] / (df_ori['BUY_VALUE_EXLARGE_ORDER_ACT'] + df_ori['BUY_VALUE_LARGE_ORDER_ACT'] + df_ori['BUY_VALUE_MED_ORDER_ACT'] + df_ori['BUY_VALUE_SMALL_ORDER_ACT'])
    return df_ori
def f_pro_bjgactdhratio(df_ori): #
    df_ori['factor'] = (df_ori['BUY_VALUE_EXLARGE_ORDER_ACT'] + df_ori['BUY_VALUE_LARGE_ORDER_ACT']) / (df_ori['BUY_VALUE_EXLARGE_ORDER_ACT'] + df_ori['BUY_VALUE_LARGE_ORDER_ACT'] + df_ori['BUY_VALUE_MED_ORDER_ACT'] + df_ori['BUY_VALUE_SMALL_ORDER_ACT'])
    return df_ori
def f_pro_bshactratio(df_ori): #
    df_ori['factor'] = (df_ori['BUY_VALUE_SMALL_ORDER_ACT']) / (df_ori['BUY_VALUE_EXLARGE_ORDER_ACT'] + df_ori['BUY_VALUE_LARGE_ORDER_ACT'] + df_ori['BUY_VALUE_MED_ORDER_ACT'] + df_ori['BUY_VALUE_SMALL_ORDER_ACT'])
    return df_ori
def f_pro_sjgact(df_ori): # SELL jg
    df_ori['factor'] = df_ori['SELL_VALUE_EXLARGE_ORDER_ACT']
    return df_ori
def f_pro_sjgactratio(df_ori): #
    df_ori['factor'] = df_ori['SELL_VALUE_EXLARGE_ORDER_ACT'] / (df_ori['SELL_VALUE_EXLARGE_ORDER_ACT'] + df_ori['SELL_VALUE_LARGE_ORDER_ACT'] + df_ori['SELL_VALUE_MED_ORDER_ACT'] + df_ori['SELL_VALUE_SMALL_ORDER_ACT'])
    return df_ori
def f_pro_sjgactdhratio(df_ori): #
    df_ori['factor'] = (df_ori['SELL_VALUE_EXLARGE_ORDER_ACT'] + df_ori['SELL_VALUE_LARGE_ORDER_ACT']) / (df_ori['SELL_VALUE_EXLARGE_ORDER_ACT'] + df_ori['SELL_VALUE_LARGE_ORDER_ACT'] + df_ori['SELL_VALUE_MED_ORDER_ACT'] + df_ori['SELL_VALUE_SMALL_ORDER_ACT'])
    return df_ori
def f_pro_sshactratio(df_ori): #
    df_ori['factor'] = (df_ori['SELL_VALUE_SMALL_ORDER_ACT']) / (df_ori['SELL_VALUE_EXLARGE_ORDER_ACT'] + df_ori['SELL_VALUE_LARGE_ORDER_ACT'] + df_ori['SELL_VALUE_MED_ORDER_ACT'] + df_ori['SELL_VALUE_SMALL_ORDER_ACT'])
    return df_ori




# 纯价格指标是否成交量加权
def f_amtstd_no(df_ori):
    return df_ori

# rolling的筛选方式
def f_roll_filter_nofilter(df_ori):
    return df_ori
# rolling后计算
def f_calc_nocalc(factor_series):
    return
def f_calc_max(factor_series):
    return factor_series[~np.isnan(factor_series)].max()
def f_calc_min(factor_series):
    return factor_series[~np.isnan(factor_series)].min()
def f_calc_avg(factor_series):
    return factor_series[~np.isnan(factor_series)].mean()
def f_calc_med(factor_series):
    return np.median(factor_series[~np.isnan(factor_series)])
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
