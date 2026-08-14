import numpy as np
import pandas as pd
# 因子属性
def f_pro_high(df_ori): # 最高价：高/pre
    df_ori['factor'] = df_ori['high'] / df_ori['pre_close']
    return df_ori
def f_pro_open(df_ori): # 开盘价：开/pre
    df_ori['factor'] = df_ori['open'] / df_ori['pre_close']
    return df_ori
def f_pro_low(df_ori): # 最低价：low/pre
    df_ori['factor'] = df_ori['low'] / df_ori['pre_close']
    return df_ori
def f_pro_close(df_ori): # 收盘价：开/pre
    df_ori['factor'] = df_ori['close'] / df_ori['pre_close']
    return df_ori
def f_pro_highori(df_ori): # 最高价
    df_ori['factor'] = df_ori['high']
    return df_ori
def f_pro_openori(df_ori): # 开盘价
    df_ori['factor'] = df_ori['open']
    return df_ori
def f_pro_lowori(df_ori): # 最低价
    df_ori['factor'] = df_ori['low']
    return df_ori
def f_pro_closeori(df_ori): # 收盘价
    df_ori['factor'] = df_ori['close']
    return df_ori
def f_pro_vwapori(df_ori): # vwap
    df_ori['factor'] = df_ori['vwap']
    return df_ori
def f_pro_pct(df_ori): # 涨幅
    df_ori['factor'] = df_ori['pct_chg']
    return df_ori
def f_pro_pctturn(df_ori): # 涨幅*turn
    df_ori['factor'] = df_ori['pct_chg'] * df_ori['turn']
    return df_ori
def f_pro_abspct(df_ori): # abs涨幅
    df_ori['factor'] = abs(df_ori['pct_chg'])
    return df_ori
def f_pro_abspctturn(df_ori): # abs涨幅 * turn
    df_ori['factor'] = abs(df_ori['pct_chg']) * df_ori['turn']
    return df_ori
def f_pro_logabspct(df_ori): # logabs涨幅
    df_ori['factor'] = np.log(abs(df_ori['pct_chg'])+0.001)
    return df_ori
def f_pro_amt(df_ori):#成交额
    df_ori['factor'] = df_ori['amt']
    return df_ori
def f_pro_turn(df_ori):#换手率
    df_ori['factor'] = df_ori['turn']
    return df_ori
def f_pro_vwap(df_ori):#均价
    df_ori['factor'] = df_ori['vwap']/df_ori['pre_close']
    return df_ori
def f_pro_syx1(df_ori): # 上影线1：(高-收)/pre
    df_ori['factor'] = (df_ori['high'] - df_ori['close']) / df_ori['pre_close']
    return df_ori
def f_pro_syx2(df_ori): # 上影线2：(高-max(开，收))/pre
    df_ori['max_open_close'] = df_ori[['open','close']].max(axis=1)
    df_ori['factor'] = (df_ori['high'] - df_ori['max_open_close']) / df_ori['pre_close']
    return df_ori
def f_pro_xyx1(df_ori): # 下影线1：(收-低)/pre
    df_ori['factor'] = (df_ori['close'] - df_ori['low']) / df_ori['pre_close']
    return df_ori
def f_pro_xyx2(df_ori): # 下影线2：(min(开，收）-低)/pre
    df_ori['min_open_close'] = df_ori[['open','close']].min(axis=1)
    df_ori['factor'] = (df_ori['min_open_close'] - df_ori['low']) / df_ori['pre_close']
    return df_ori
def f_pro_syx2xyx1(df_ori):
    df_ori['syx1'] = (df_ori['high'] - df_ori['close']) / df_ori['pre_close']
    df_ori['xyx1'] = (df_ori['close'] - df_ori['low']) / df_ori['pre_close']
    df_ori['factor'] = df_ori['syx1'] - df_ori['xyx1']
    return df_ori
def f_pro_syx2xyx2(df_ori):
    df_ori['max_open_close'] = df_ori[['open', 'close']].max(axis=1)
    df_ori['min_open_close'] = df_ori[['open', 'close']].min(axis=1)
    df_ori['syx2'] = (df_ori['high'] - df_ori['max_open_close']) / df_ori['pre_close']
    df_ori['xyx2'] = (df_ori['min_open_close'] - df_ori['low']) / df_ori['pre_close']
    df_ori['factor'] = df_ori['syx2'] - df_ori['xyx2']
    return df_ori
def f_pro_lengthk(df_ori):# k线柱长 abs(开-收)/pre
    df_ori['factor'] = abs(df_ori['open'] - df_ori['close']) / df_ori['pre_close']
    return df_ori
def f_pro_c2v(df_ori):#close/vwap
    df_ori['factor'] = df_ori['close'] / df_ori['vwap']
    return df_ori
def f_pro_h2v(df_ori):#high/vwap
    df_ori['factor'] = df_ori['high'] / df_ori['vwap']
    return df_ori
def f_pro_l2v(df_ori):#low/vwap
    df_ori['factor'] = df_ori['low'] / df_ori['vwap']
    return df_ori
def f_pro_amp(df_ori):#振幅
    df_ori['factor'] = (df_ori['high'] - df_ori['low']) / df_ori['pre_close']
    return df_ori
def f_pro_corrv2c20(df_ori):#corr:vwap & close
    x = 'vwap'
    y = 'close'
    df_ori['xy'] = df_ori[x] * df_ori[y]
    df_ori['exy'] = df_ori['xy'].unstack().rolling(20,5).mean().stack()
    df_ori['ex'] = df_ori[x].unstack().rolling(20,5).mean().stack()
    df_ori['ey'] = df_ori[y].unstack().rolling(20,5).mean().stack()
    df_ori['stdx'] = df_ori[x].unstack().rolling(20,5).std().stack()
    df_ori['stdy'] = df_ori[y].unstack().rolling(20,5).std().stack()
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])\
                       /(df_ori['stdx'] * df_ori['stdy'])
    df_ori['factor'] = df_ori['factor'].apply(lambda x: 1 if x > 1.0001 else -1 if x < -1.0001 else x)
    return df_ori
def f_pro_corramt2c20(df_ori):#corr:amt & close
    x = 'amt'
    y = 'close'
    df_ori['xy'] = df_ori[x] * df_ori[y]
    df_ori['exy'] = df_ori['xy'].unstack().rolling(20,5).mean().stack()
    df_ori['ex'] = df_ori[x].unstack().rolling(20,5).mean().stack()
    df_ori['ey'] = df_ori[y].unstack().rolling(20,5).mean().stack()
    df_ori['stdx'] = df_ori[x].unstack().rolling(20,5).std().stack()
    df_ori['stdy'] = df_ori[y].unstack().rolling(20,5).std().stack()
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])\
                       /(df_ori['stdx'] * df_ori['stdy'])
    df_ori['factor'] = df_ori['factor'].apply(lambda x : 1 if x > 1.0001 else -1 if x < -1.0001 else x)
    return df_ori
def f_pro_corramt2syx20(df_ori):#corr:amt & syx1
    x = 'amt'
    y = 'syx1'
    df_ori[y] = (df_ori['high'] - df_ori['close']) / df_ori['pre_close']
    df_ori['xy'] = df_ori[x] * df_ori[y]
    df_ori['exy'] = df_ori['xy'].unstack().rolling(20,5).mean().stack()
    df_ori['ex'] = df_ori[x].unstack().rolling(20,5).mean().stack()
    df_ori['ey'] = df_ori[y].unstack().rolling(20,5).mean().stack()
    df_ori['stdx'] = df_ori[x].unstack().rolling(20,5).std().stack()
    df_ori['stdy'] = df_ori[y].unstack().rolling(20,5).std().stack()
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])\
                       /(df_ori['stdx'] * df_ori['stdy'])
    df_ori['factor'] = df_ori['factor'].apply(lambda x: 1 if x > 1.0001 else -1 if x < -1.0001 else x)
    return df_ori
def f_pro_corramt2xyx20(df_ori):#corr:amt & xyx1
    x = 'amt'
    y = 'xyx1'
    df_ori[y] = (df_ori['close'] - df_ori['low']) / df_ori['pre_close']
    df_ori['xy'] = df_ori[x] * df_ori[y]
    df_ori['exy'] = df_ori['xy'].unstack().rolling(20,5).mean().stack()
    df_ori['ex'] = df_ori[x].unstack().rolling(20,5).mean().stack()
    df_ori['ey'] = df_ori[y].unstack().rolling(20,5).mean().stack()
    df_ori['stdx'] = df_ori[x].unstack().rolling(20,5).std().stack()
    df_ori['stdy'] = df_ori[y].unstack().rolling(20,5).std().stack()
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])\
                       /(df_ori['stdx'] * df_ori['stdy'])
    df_ori['factor'] = df_ori['factor'].apply(lambda x: 1 if x > 1.0001 else -1 if x < -1.0001 else x)
    return df_ori
def f_pro_corrpct2syx20(df_ori):#corr:pct & syx
    x = 'pct_chg'
    y = 'syx1'
    df_ori[y] = (df_ori['high'] - df_ori['close']) / df_ori['pre_close']
    df_ori['xy'] = df_ori[x] * df_ori[y]
    df_ori['exy'] = df_ori['xy'].unstack().rolling(20,5).mean().stack()
    df_ori['ex'] = df_ori[x].unstack().rolling(20,5).mean().stack()
    df_ori['ey'] = df_ori[y].unstack().rolling(20,5).mean().stack()
    df_ori['stdx'] = df_ori[x].unstack().rolling(20,5).std().stack()
    df_ori['stdy'] = df_ori[y].unstack().rolling(20,5).std().stack()
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])\
                       /(df_ori['stdx'] * df_ori['stdy'])
    df_ori['factor'] = df_ori['factor'].apply(lambda x: 1 if x > 1.0001 else -1 if x < -1.0001 else x)
    return df_ori
def f_pro_corrpct2xyx20(df_ori):#corr:pct & xyx1
    x = 'pct_chg'
    y = 'xyx1'
    df_ori[y] = (df_ori['close'] - df_ori['low']) / df_ori['pre_close']
    df_ori['xy'] = df_ori[x] * df_ori[y]
    df_ori['exy'] = df_ori['xy'].unstack().rolling(20,5).mean().stack()
    df_ori['ex'] = df_ori[x].unstack().rolling(20,5).mean().stack()
    df_ori['ey'] = df_ori[y].unstack().rolling(20,5).mean().stack()
    df_ori['stdx'] = df_ori[x].unstack().rolling(20,5).std().stack()
    df_ori['stdy'] = df_ori[y].unstack().rolling(20,5).std().stack()
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])\
                       /(df_ori['stdx'] * df_ori['stdy'])
    df_ori['factor'] = df_ori['factor'].apply(lambda x: 1 if x > 1.0001 else -1 if x < -1.0001 else x)
    return df_ori
def f_pro_pctnew1(df_ori):
    df_ori['factor'] = (df_ori['close'] - df_ori['pre_close'])/(df_ori['high'] + df_ori['low'])*2
    return df_ori
def f_pro_pctnew2(df_ori):
    df_ori['factor'] = (df_ori['close'] - df_ori['pre_close'])/(df_ori['vwap'])
    return df_ori
def f_pro_o2a(df_ori):#open/amt
    df_ori['factor'] = df_ori['open'] / df_ori['amt']
    return df_ori
def f_pro_c2a(df_ori):#close/amt
    df_ori['factor'] = df_ori['close'] / df_ori['amt']
    return df_ori
def f_pro_pre2vol(df_ori):#pre/volume
    df_ori['factor'] = df_ori['pre_close'] / df_ori['volume']
    return df_ori
# 纯价格指标是否成交量加权
def f_amtstd_no(df_ori):
    return df_ori
def f_amtstd_yes(df_ori): # 如果需要，必须有指标2，指标2必须是amt
    df_ori['factor'] = df_ori['factor'] * df_ori['amt']
    return df_ori
# rolling的筛选方式
def f_roll_filter_nofilter(df_ori):
    return df_ori
def f_roll_filter_up1(df_ori): # 只取上涨，其他为nan
    df_ori['up'] = np.sign(df_ori['pct_chg'])
    df_ori['up'] = df_ori['up'].apply(lambda x : 1 if x >= 0.5 else np.nan)
    df_ori['factor'] = df_ori['factor'] * df_ori['up']
    return df_ori
def f_roll_filter_down1(df_ori): # 只取下跌，其他为nan
    df_ori['down'] = np.sign(df_ori['pct_chg'])
    df_ori['down'] = df_ori['down'].apply(lambda x : -1 if x <= -0.5 else np.nan)
    df_ori['factor'] = df_ori['factor'] * df_ori['down']
    return df_ori
def f_roll_filter_up2(df_ori): # 上涨为1，下跌为-1
    df_ori['up'] = np.sign(df_ori['pct_chg'])
    df_ori['up'] = df_ori['up'].apply(lambda x : 1 if x >= 0.5 else -1 if x <=-0.5 else 0)
    df_ori['factor'] = df_ori['factor'] * df_ori['up']
    return df_ori
def f_roll_filter_amtup201(df_ori):# 成交量在20日线以上取1，其余nan
    df_ori['amt20'] = df_ori['amt'].unstack().rolling(20,1).mean().stack()
    df_ori['amtup20'] = np.sign(df_ori['amt'] - df_ori['amt20'])
    df_ori['amtup20'] = df_ori['amtup20'].apply(lambda x :  1 if x >= 0.5 else np.nan)
    df_ori['factor'] = df_ori['factor'] * df_ori['amtup20']
    return df_ori
def f_roll_filter_amtdown201(df_ori):# 成交量在20日线以下取-1，其余nan
    df_ori['amt20'] = df_ori['amt'].unstack().rolling(20,1).mean().stack()
    df_ori['amtup20'] = np.sign(df_ori['amt'] - df_ori['amt20'])
    df_ori['amtup20'] = df_ori['amtup20'].apply(lambda x :  -1 if x <= -0.5 else np.nan)
    df_ori['factor'] = df_ori['factor'] * df_ori['amtup20']
    return df_ori
def f_roll_filter_amtup202(df_ori):# 成交量在20日线以上取1，其余同理0和-1
    df_ori['amt20'] = df_ori['amt'].unstack().rolling(20,1).mean().stack()
    df_ori['amtup20'] = np.sign(df_ori['amt'] - df_ori['amt20'])
    df_ori['factor'] = df_ori['factor'] * df_ori['amtup20']
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
# 生成核函数
def f_ABC_0(df_ori,col):
    df_ori[col] = 0
    return df_ori
def f_ABC_high(df_ori,col):
    df_ori[col] = df_ori['high']
    return df_ori
def f_ABC_open(df_ori,col):
    df_ori[col] = df_ori['open']
    return df_ori
def f_ABC_low(df_ori,col):
    df_ori[col] = df_ori['low']
    return df_ori
def f_ABC_close(df_ori,col):
    df_ori[col] = df_ori['close']
    return df_ori
def f_ABC_vwap(df_ori,col):
    df_ori[col] = df_ori['vwap']
    return df_ori
def f_ABC_pre(df_ori,col):
    df_ori[col] = df_ori['pre_close']
    return df_ori
def f_ABC_hl(df_ori,col):
    df_ori[col] = (df_ori['high'] + df_ori['low']) * 0.5
    return df_ori
def f_ABC_oc(df_ori,col):
    df_ori[col] = (df_ori['open'] + df_ori['close']) * 0.5
    return df_ori