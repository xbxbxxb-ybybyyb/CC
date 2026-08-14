import numpy as np
import pandas as pd
import decimal

def round_(x, n=0):
    x = x + 1e-10
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res
# 因子属性
def f_pro_high(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = df_high
    return df
def f_pro_open(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = df_open
    return df
def f_pro_close(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = df_close
    return df
def f_pro_low(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = df_low
    return df
def f_pro_amt(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = df_amt
    return df
def f_pro_volume(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = df_volume
    return df
def f_pro_h2p(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = df_high.divide(df_pre, axis=0)
    return df
def f_pro_l2p(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = df_low.divide(df_pre, axis=0)
    return df
def f_pro_c2p(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = df_close.divide(df_pre, axis=0)
    return df
def f_pro_h2c(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = df_high / df_close
    return df
def f_pro_l2c(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = df_low / df_close
    return df
def f_pro_hl2p(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = (df_high - df_low).divide(df_pre, axis=0)
    return df
def f_pro_vwap(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df_vwap = df_amt.cumsum(axis=1) / df_volume.cumsum(axis=1)
    return df_vwap
def f_pro_c2v(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df_vwap = df_amt.cumsum(axis=1) / df_volume.cumsum(axis=1)
    df = df_close / df_vwap
    return df
def f_pro_h2v(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df_vwap = df_amt.cumsum(axis=1) / df_volume.cumsum(axis=1)
    df = df_high / df_vwap
    return df
def f_pro_l2v(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df_vwap = df_amt.cumsum(axis=1) / df_volume.cumsum(axis=1)
    df = df_low / df_vwap
    return df
def f_pro_abspct(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = abs(df_close.divide(df_pre, axis=0))
    return df
def f_pro_logabspct(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = np.log(abs(df_close.divide(df_pre, axis=0)) + 1e-3)
    return df
def f_pro_abspctamt(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = abs(df_close.divide(df_pre, axis=0)) * df_amt
    return df
def f_pro_syx1(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = (df_high - df_close).divide(df_pre, axis=0)
    return df
def f_pro_syx2(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,):  #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = (df_high - df_close.clip(lower=df_open)).divide(df_pre, axis=0)
    return df
def f_pro_xyx1(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,):  #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = (df_close - df_low).divide(df_pre, axis=0)
    return df
def f_pro_xyx2(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,):  #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = (df_close - df_close.clip(upper=df_open)).divide(df_pre, axis=0)
    return df
def f_pro_lengthk(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,):  #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = abs(df_open - df_close).divide(df_pre, axis=0)
    return df
#
def f_pro_closediff(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,):  #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = df_close.diff(axis=1).fillna(0).divide(df_pre, axis=0)
    return df
def f_pro_absclosediff(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,):  #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = abs(df_close.diff(axis=1).fillna(0)).divide(df_pre, axis=0)
    return df
def f_pro_voldiff(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,):  #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = df_volume.diff(axis=1).fillna(0).divide(df_volume.sum(axis=1), axis=0)
    return df
def f_pro_absvoldiff(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,):  #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = abs(df_volume.diff(axis=1).fillna(0)).divide(df_volume.sum(axis=1), axis=0)
    return df
# === 5min 的pro ===
def f_pro_bqty(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = df_bqty
    return df
def f_pro_bqtydiff2tvol(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = df_bqty.diff(axis=1).fillna(0).divide(df_volume.sum(axis=1), axis=0)
    return df
def f_pro_sqty(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = df_sqty
    return df
def f_pro_sqtydiff2tvol(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = df_sqty.diff(axis=1).fillna(0).divide(df_volume.sum(axis=1), axis=0)
    return df
def f_pro_bp(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = df_bp
    return df
def f_pro_sp(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = df_sp
    return df
def f_pro_bp2sp(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = (df_bp - df_sp).divide(df_pre, axis=0)
    return df
def f_pro_bqtyratio(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = (df_bqty) / (df_bqty + df_sqty)
    return df
def f_pro_bqty2sqty(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = (df_bqty - df_sqty) / (df_bqty + df_sqty)
    return df
def f_pro_absbqty2sqty(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = abs(df_bqty - df_sqty) / (df_bqty + df_sqty)
    return df
def f_pro_c2bp(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = (df_close - df_bp).divide(df_pre, axis=0)
    return df
def f_pro_c2sp(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
    df = (df_close - df_sp).divide(df_pre, axis=0)
    return df
def f_pro_v2bqty(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = (df_volume) / (df_bqty + 1)
    return df
def f_pro_v2sqty(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = (df_volume) / (df_sqty + 1)
    return df
def f_pro_v2bsqty(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = (df_volume) / (df_sqty + df_bqty + 1)
    return df
def f_pro_amt2bamt(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = (df_amt) / (df_bqty * df_bp + 1)
    return df
def f_pro_amt2samt(df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,): #
    df = (df_amt) / (df_sqty * df_sp + 1)
    return df
# 筛选
def f_filter_nofilter(df, df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,):
    return df
def f_filter_up(df, df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,):
    df_close_delta = df_close.T.apply(lambda x : x - x.shift(1)).T.applymap(lambda x : round_(x,5))
    df_sign = df_close_delta.applymap(lambda x : 1 if x > 0 else np.nan)
    df = df * df_sign
    return df
def f_filter_down(df, df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,):
    df_close_delta = df_close.T.apply(lambda x : x - x.shift(1)).T.applymap(lambda x : round_(x,5))
    df_sign = df_close_delta.applymap(lambda x : 1 if x < 0 else np.nan)
    df = df * df_sign
    return df
# 横向加权变量
def f_day_div_no(df, df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,):
    return df
def f_day_div_amt(df, df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,):
    return df * df_amt
def f_day_div_volume(df, df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,):
    return df * df_volume
def f_day_div_close(df, df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,):
    return df * df_close
# 分母df
def get_fm_df(day_div, df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,):
    res = {
        'amt': df_amt,
        'volume': df_volume,
        'close':df_close
    }
    return res[day_div]
# 横纵向计算函数
def f_calc_nocalc(factor_series):
    return
def f_calc_absmax(factor_series):
    return abs(factor_series[~np.isnan(factor_series)]).max()
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
    if abs(f_calc_sum(factor_series)) > 1e-8:
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
    factor_series = factor_series[~np.isnan(factor_series)]
    try:
        res = factor_series[-1] - factor_series[0]
    except:
        res = np.nan
    return res
def f_calc_m2m(factor_series):
    factor_series = factor_series[~np.isnan(factor_series)]
    return factor_series.max() / factor_series.mean() if (factor_series.mean() * factor_series.max())>0 and abs(factor_series.mean()) > 1e-6 else np.nan
def f_calc_pos(factor_series):
    factor_series = factor_series[~np.isnan(factor_series)]
    return (factor_series[-1] - factor_series.min()) / \
           (factor_series.max() - factor_series.min() + 1e-8)
def f_calc_std(factor_series):
    factor_series = factor_series[~np.isnan(factor_series)]
    return np.std(factor_series,ddof=1)
