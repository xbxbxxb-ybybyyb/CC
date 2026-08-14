import gc
import psutil
import pandas as pd
import numpy as np
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from dataApi.getData import get_minute_1factor, get_daily_1factor
from dataApi.testFactor import FactorBackTest

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

start_date = 20170103
end_date = 20191231
shift = 20
short_ret_days = 2
vol_refer_time = 20

ft = FactorBackTest(start_date, end_date)

vol = get_minute_1factor('vol', start_date, end_date)
columns = vol.columns
index = [int(x[0] * 10000 + x[1]) for x in vol.index]

ret_daily = get_daily_1factor('pct_chg', get_date_range(
    get_pre_trade_date(start_date, shift), get_pre_trade_date(end_date))).reindex(columns=columns) / 100
amt_daily = get_daily_1factor('amt', get_date_range(
    get_pre_trade_date(start_date, shift), get_pre_trade_date(end_date))).reindex(columns=columns) > 1
pre_close = get_daily_1factor('pre_close', get_date_range(start_date, end_date)).reindex(columns=columns).values
ret_daily = ret_daily[amt_daily].values

ret1 = np.expm1(np.apply_along_axis(np.convolve, 0, np.log1p(ret_daily), np.ones(shift), 'valid'))
ret1 = np.argsort(np.argsort(ret1)) / (~np.isnan(ret1)).sum(axis=0)

ret2 = np.abs(np.expm1(np.apply_along_axis(np.convolve, 0, np.log1p(ret_daily[shift - short_ret_days:]),
                                           np.ones(short_ret_days), 'valid')))
ret2 = np.argsort(np.argsort(ret2)) / (~np.isnan(ret2)).sum(axis=0)

vol = vol.values
vol_refer = np.apply_along_axis(np.convolve, 0, vol, np.ones(vol_refer_time) / vol_refer_time, 'same')
vol_refer = (vol / vol_refer).reshape(vol.shape[0] // 242, 242, vol.shape[1])

high = get_minute_1factor('high', start_date, end_date).values.reshape(vol_refer.shape).swapaxes(0, 1)
low = get_minute_1factor('low', start_date, end_date).values.reshape(vol_refer.shape).swapaxes(0, 1)
close = get_minute_1factor('close', start_date, end_date).values.reshape(vol_refer.shape).swapaxes(0, 1)
open = get_minute_1factor('open', start_date, end_date).values.reshape(vol_refer.shape).swapaxes(0, 1)
vol_refer = vol_refer.swapaxes(0, 1)

close_bench = get_minute_1factor('close', start_date, end_date, code_list=['ZZ500'], type='bench').iloc[:, 0].values
close_bench = close_bench.reshape(close_bench.shape[0] // 242, 242).swapaxes(0, 1)
pre_close_bench = get_daily_1factor('close', get_date_range(
    get_pre_trade_date(start_date), get_pre_trade_date(end_date)), code_list=['ZZ500'], type='bench').iloc[:, 0].values
ret3 = close / pre_close - np.expand_dims(close_bench / pre_close_bench, axis=2).repeat(close.shape[2], axis=2)

buy = (True
    & (ret1 < 0.3)
    & (ret2 < 0.8)
    & (vol_refer > 2)
    & (close - open > 0)
    & ((high - close) / (high - low) < 0.3)
).swapaxes(0, 1)

sell = ((~ buy.swapaxes(0, 1))
    & (ret3 > 0.03)
).swapaxes(0, 1)

sign = (buy * 1 - sell * 1).reshape(buy.shape[0] * buy.shape[1], buy.shape[2])
sign = pd.DataFrame(sign, index=index, columns=columns)

ft.evaluate(sign)
ft.result

###
from BackTestModule.QuickFactorEvaluationBackTest import FactorBackTest
factor_test = FactorBackTest(sign)
factor_test.evaluation(23)
factor_test.result_output('high_volume', fileroot='/data/user/015836/')