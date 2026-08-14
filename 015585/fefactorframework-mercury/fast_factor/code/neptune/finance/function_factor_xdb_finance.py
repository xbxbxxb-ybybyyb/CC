import numpy as np
import pandas as pd
import decimal

def get_time_delta(itime):
    mls = int(str(int(itime))[-3:])
    s = int(str(int(itime))[-5:-3])
    m = int(str(int(itime))[-7:-5])
    h = int(str(int(itime))[:-7])
    time_mls = h * 3600 * 1000 + m * 60 * 1000 + s * 1000 + mls
    time_mls_900 = 9 * 3600 * 1000
    if int(itime) > 120000000:
        time_delta = time_mls - time_mls_900 - 5400000
    else:
        time_delta = time_mls - time_mls_900
    return time_delta
def round_(x, n=0):
    x = x + 1e-10
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res
# 因子属性函数
def f_pro_amt(fin_df):
    cancel_df['OrderAmt'] = cancel_df['OrderPrice'] * cancel_df['OrderQty']
    return cancel_df['OrderAmt']
# 季度筛选函数，返回df
def f_t_kind_cum(fin_df):
    return fin_df
def f_t_kind_single(fin_df):
    columns = fin_df.columns
    columns = [x for x in columns if x not in ['ANN_DT','']]
    for col in columns:
        fin_df[f'{col}_diff'] = fin_df.groupby(['dt', 'Ticker'])['OPER_REV'].diff()
    fin_df.loc[fin_df['report_period'] == 1, 'OPER_REV_diff'] = fin_df.loc[
        fin_df['report_period'] == 1, 'OPER_REV']




# 标准化处理,计算序列值
def f_calc_amp(factor_series):
    return factor_series[~np.isnan(factor_series)].max() - factor_series[~np.isnan(factor_series)].min()
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