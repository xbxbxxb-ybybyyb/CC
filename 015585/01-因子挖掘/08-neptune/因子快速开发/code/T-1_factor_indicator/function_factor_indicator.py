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
def f_pro_pe(df_ori): #
    df_ori['factor'] = df_ori['S_VAL_PE']
    return df_ori
def f_pro_pb(df_ori): #
    df_ori['factor'] = df_ori['S_VAL_PB_NEW']
    return df_ori
def f_pro_pettm(df_ori): #
    df_ori['factor'] = df_ori['S_VAL_PE_TTM']
    return df_ori
def f_pro_pcfocf(df_ori): #
    df_ori['factor'] = df_ori['S_VAL_PCF_OCF']
    return df_ori
def f_pro_pcfocfttm(df_ori): #
    df_ori['factor'] = df_ori['S_VAL_PCF_OCFTTM']
    return df_ori
def f_pro_pcfncf(df_ori): #
    df_ori['factor'] = df_ori['S_VAL_PCF_NCF']
    return df_ori
def f_pro_pcfncfttm(df_ori): #
    df_ori['factor'] = df_ori['S_VAL_PCF_NCFTTM']
    return df_ori
def f_pro_ps(df_ori): #
    df_ori['factor'] = df_ori['S_VAL_PS']
    return df_ori
def f_pro_psttm(df_ori): #
    df_ori['factor'] = df_ori['S_VAL_PS_TTM']
    return df_ori
def f_pro_p2dps(df_ori): #
    df_ori['factor'] = df_ori['S_PRICE_DIV_DPS']
    return df_ori
def f_pro_nppcttm(df_ori): #归属母公司净利润
    df_ori['factor'] = df_ori['NET_PROFIT_PARENT_COMP_TTM']
    return df_ori
def f_pro_nppclyr(df_ori): #
    df_ori['factor'] = df_ori['NET_PROFIT_PARENT_COMP_LYR']
    return df_ori
def f_pro_nassets(df_ori): #当日净资产
    df_ori['factor'] = df_ori['NET_ASSETS_TODAY']
    return df_ori
def f_pro_ncfoattm(df_ori): # 经营活动产生的现金流量净额
    df_ori['factor'] = df_ori['NET_CASH_FLOWS_OPER_ACT_TTM']
    return df_ori
def f_pro_ncfoalyr(df_ori): #
    df_ori['factor'] = df_ori['NET_CASH_FLOWS_OPER_ACT_LYR']
    return df_ori
def f_pro_orttm(df_ori): # 营业收入(TTM)
    df_ori['factor'] = df_ori['OPER_REV_TTM']
    return df_ori
def f_pro_orlyr(df_ori):
    df_ori['factor'] = df_ori['OPER_REV_LYR']
    return df_ori
def f_pro_niccettm(df_ori):
    df_ori['factor'] = df_ori['NET_INCR_CASH_CASH_EQU_TTM']
    return df_ori
def f_pro_niccelyr(df_ori):
    df_ori['factor'] = df_ori['NET_INCR_CASH_CASH_EQU_LYR']
    return df_ori
# 筛选
def f_filter_nofilter(df_ori):
    return df_ori
# 计算函数
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
    return factor_series.max() / factor_series.mean() if factor_series.mean()>0 else np.nan
def f_calc_pos(factor_series):
    factor_series = factor_series[~np.isnan(factor_series)]
    return (factor_series[-1] - factor_series.min()) / \
           (factor_series.max() - factor_series.min() + 1e-8)
def f_calc_std(factor_series):
    factor_series = factor_series[~np.isnan(factor_series)]
    return np.std(factor_series,ddof=1)
