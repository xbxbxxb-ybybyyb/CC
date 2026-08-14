import gc
import psutil
import pandas as pd
import numpy as np
from tqdm import tqdm
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from dataApi.getData import get_minute_1factor, get_minute_return, get_daily_1factor
from dataApi.testFactor import FactorBackTest
import time

def _rolling_windows(a, window):
    """Creates rolling-window 'blocks' of length `window` from `a`.
    Note that the orientation of rows/columns follows that of pandas.
    Example
    -------
    import numpy as np
    onedim = np.arange(20)
    twodim = onedim.reshape((5,4))
    print(twodim)
    [[ 0  1  2  3]
     [ 4  5  6  7]
     [ 8  9 10 11]
     [12 13 14 15]
     [16 17 18 19]]
    print(rwindows(onedim, 3)[:5])
    [[0 1 2]
     [1 2 3]
     [2 3 4]
     [3 4 5]
     [4 5 6]]
    print(rwindows(twodim, 3)[:5])
    [[[ 0  1  2  3]
      [ 4  5  6  7]
      [ 8  9 10 11]]
     [[ 4  5  6  7]
      [ 8  9 10 11]
      [12 13 14 15]]
     [[ 8  9 10 11]
      [12 13 14 15]
      [16 17 18 19]]]
    """

    if window > a.shape[0]:
        raise ValueError(
            "Specified `window` length of {0} exceeds length of"
            " `a`, {1}.".format(window, a.shape[0])
        )
    if isinstance(a, (pd.Series, pd.DataFrame)):
        a = a.values
    if a.ndim == 1:
        a = a.reshape(-1, 1)
    shape = (a.shape[0] - window + 1, window) + a.shape[1:]
    strides = (a.strides[0],) + a.strides
    windows = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    if windows.ndim == 1:
        windows = np.atleast_2d(windows)
    return windows

def _memory_used():

    info = psutil.virtual_memory()
    used = round((info.total - info.available) / 1024 ** 3, 2)
    return used

def calc_corr(arr):

    corr = np.empty((arr.shape[0], arr.shape[1], arr.shape[1]))
    for j in tqdm(range(arr.shape[0])):
        corr[j] = np.corrcoef(arr[j, ...])
    return corr

t = time.time()
time.time() - t

minute_interval = 5
window = 10
top_stock = 3
start_date = 20161201
end_date = 20191230

ft = FactorBackTest(start_date, end_date)
ret = get_minute_return(minute_interval, start_date, get_pre_trade_date(end_date))
ret_columns = ret.columns
freq = 240 // minute_interval
ret = ret.values.reshape(ret.shape[0] // freq, freq, ret.shape[1])
ret = _rolling_windows(ret, window)
ret = ret.reshape(ret.shape[0], ret.shape[1] * ret.shape[2], ret.shape[3]).swapaxes(0, 1)
np.add(ret, 1, out=ret)
np.log(ret, out=ret)
ret = ret.swapaxes(0, 1).swapaxes(1, 2)
t = time.time()
corr = np.vectorize(np.corrcoef, signature='(n,k)->(n,n)')(ret)
print(time.time() - t)
del corr
gc.collect()
t = time.time()
corr = calc_corr(ret)
print(time.time() - t)
corr[np.isnan(corr)] = 0
corr_rank = np.argpartition(corr, (-1, - top_stock - 1), axis=-1)[..., - top_stock - 1:-1]
corr = np.partition(corr, (-1, - top_stock - 1), axis=-1)[..., - top_stock - 1:-1]
corr = np.nanmean(corr, axis=2)

ret = get_minute_return(1, get_pre_trade_date(start_date, - window), end_date)
ret_index = [int(x[0] * 10000 + x[1]) for x in ret.index]
ret = np.log(ret.values.reshape(ret.shape[0] // 242, 242, ret.shape[1]).swapaxes(1, 2) + 1)
refer = ret[np.arange(ret.shape[0])[:, None, None], corr_rank, :]
refer = np.nanmean(refer, axis=2)
ret_excess = np.nancumsum(ret, axis=2) - np.nancumsum(refer, axis=2)

ret_daily = get_daily_1factor('pct_chg', get_date_range(
    get_pre_trade_date(start_date, - window + 1), get_pre_trade_date(end_date)), ret_columns.to_list()).values / 100
refer_daily = np.log(ret_daily[np.arange(ret.shape[0])[:, None, None], corr_rank] + 1)
refer_daily = np.nanmean(refer_daily, axis=2)
ret_daily_excess = ret_daily - refer_daily

bench = get_minute_1factor('close', get_pre_trade_date(start_date, - window + 1) * 10000 + 1500, end_date,
                           code_list=['ZZ500'], type='bench').pct_change().iloc[1:,0]
bench = np.log(bench.values.reshape(bench.shape[0] // 242, 242) + 1)
bench = np.nancumsum(bench, axis=1)
ret_bench = (np.nancumsum(ret, axis=2).swapaxes(0, 1) - bench).swapaxes(0, 1)


buy = (
        (ret_excess.swapaxes(0, 2).swapaxes(1, 2) < -0.03) &
        (corr >= 0.3) &
        (ret_bench.swapaxes(0, 2).swapaxes(1, 2) <= 0) &
        (ret_daily_excess < 0) &
        (ret_daily_excess > -0.03) &
        (ret_bench.swapaxes(0, 2).swapaxes(1, 2) > -0.03)
).swapaxes(0, 1)

sell = (
        (ret_excess.swapaxes(0, 2).swapaxes(1, 2) > 0.06) &
        (~ buy.swapaxes(0, 1))
).swapaxes(0, 1)

sign = (buy * 1 - sell * 1).reshape(buy.shape[0] * buy.shape[1], buy.shape[2])
sign = pd.DataFrame(sign, index=ret_index, columns=ret_columns)


from BackTestModule.QuickFactorEvaluationBackTest import FactorBackTest
factor_test = FactorBackTest(sign)
factor_test.evaluation(23)
factor_test.result_output('corrcoef', fileroot='/data/user/015836/')


ft.evaluate(sign)
ft.result
