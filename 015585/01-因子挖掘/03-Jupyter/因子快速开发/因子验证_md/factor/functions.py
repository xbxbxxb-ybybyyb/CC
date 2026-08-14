import numpy as np
import pandas as pd
import decimal
import datetime as dt
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

def fun_get_time(time1,sec_delta):
    tmp_time = dt.datetime.strptime(str(time1)[:-3],'%H%M%S')
    tmp_time2 = tmp_time+dt.timedelta(seconds=sec_delta)
    tmp_time2_str = tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
    if (int(tmp_time2_str)>113000000)&(time1<=113000000):
        adj_tmp_time2 = tmp_time2+dt.timedelta(seconds=1.5*3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str)<130000000)&(time1>=130000000):
        adj_tmp_time2 = tmp_time2-dt.timedelta(seconds=1.5*3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str)<93000000)&(time1>=93000000):
        adj_tmp_time2_str = '92500000'
        return int(adj_tmp_time2_str)
    elif (time1<93000000):
        adj_tmp_time2 = tmp_time2+dt.timedelta(seconds=4*60)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
        return int(adj_tmp_time2_str)
    else:
        return int(tmp_time2_str)
def round_(x, n=0):
    x = x + 1e-10
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res