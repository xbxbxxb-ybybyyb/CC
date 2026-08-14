import numpy as np
import pandas as pd
import decimal
import datetime as dt
def f_calc_max(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.max()
def f_calc_min(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.min()
def f_calc_avg(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.mean()
def f_calc_med(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.median()
def f_calc_cv(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        if  abs(tick_series.mean()) > 0.0001:
            return tick_series.std() / tick_series.mean()
        else:
            return np.nan
def f_calc_sum(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.sum()
def f_calc_cct(tick_series):
    if abs(tick_series.sum()) > 0.001:
        return (tick_series**2).sum() / (tick_series.sum())**2
    else:
        return np.nan
def f_calc_skew(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.skew()
def f_calc_kurt(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.kurt()
def f_calc_change(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.head(1).mean() - tick_series.tail(1).mean()
def f_calc_tail(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.tail(1).mean()
def f_calc_m2m(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.max() / tick_series.mean() if (tick_series.min() >= 0 or tick_series.max() <= 0) else np.nan
def f_calc_std(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.std()
def f_calc_length(tick_series):
    return len(tick_series)
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