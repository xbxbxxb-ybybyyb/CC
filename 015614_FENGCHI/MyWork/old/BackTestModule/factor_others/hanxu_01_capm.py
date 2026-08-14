import gc
import psutil
#psutil.virtual_memory()
import math
import pandas as pd
import numpy as np
from dataApi.tradeDate import get_date_range
from dataApi.getData import get_minute_1factor, get_minute_return, get_daily_1factor
from dataApi.testFactor import FactorBackTest
ft = FactorBackTest()
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

minute_interval = 5
window = 10
boll_day = 2
bench = 'ZZ500'

ret = get_minute_return(minute_interval=minute_interval)
ret_bench = get_minute_1factor('close_%sm' % minute_interval, minute_interval=minute_interval,
                                 code_list=[bench], type='bench').pct_change()
ret = np.log(1 + ret)
ret_bench = np.log(1 + ret_bench)

n = 240 // minute_interval
r0 = np.abs(ret_bench.T.values)
r1 = np.abs(ret.T.values + ret_bench.iloc[:,0].values)
r2 = np.abs(ret.T.values - ret_bench.iloc[:,0].values)
num = r1.shape[0]
r = np.r_[r0, r1, r2]
r = r.reshape(r.shape[0], r.shape[1] // n, n)
del r0, r1, r2
gc.collect()

coef = 2.5 * n ** (-0.49)
RV = (r ** 2).sum(axis=-1)
BV = math.pi / 2 * (r[..., :-1] * r[..., 1:]).sum(axis=-1)
TOD = (r.swapaxes(0, 1).swapaxes(0, -1) <= coef * np.sqrt(np.minimum(RV, BV))).swapaxes(0, -1).swapaxes(0, 1) * r ** 2
TOD = _rolling_windows(TOD.swapaxes(0, 1), window).sum(axis=1)
TOD = n * TOD.swapaxes(0, -1) / TOD.sum(axis=-1).swapaxes(0, -1)
k = np.sqrt(np.expand_dims(_rolling_windows(np.minimum(RV, BV).swapaxes(0, -1), window), axis=0).repeat(n, axis=0).
             swapaxes(1, 3) * np.expand_dims(TOD, axis=2).repeat(window, axis=2)) * coef
del coef, RV, BV, TOD
gc.collect()

r = _rolling_windows(r.swapaxes(0, 1), window).swapaxes(0, 2).swapaxes(1, 2)
k = k.swapaxes(0, 1).swapaxes(1, 3)

beta1 = ((r[1:num+1] ** 2 * (r[1:num+1] <= k[1:num+1]) - r[num+1:] ** 2 * (r[num+1:] <= k[num+1:])).
         sum(axis=-1).sum(axis=-1)) / (4 * (r[0] ** 2 * (r[0] <= k[0])).squeeze().sum(axis=-1).sum(axis=-1))
beta2 = ((r[1:num+1] * r[0].squeeze()) ** 2).sum(axis=-1).sum(axis=-1) / (r[0].squeeze() ** 4).sum(axis=-1).sum(axis=-1)

index = sorted(list(set(ret_bench.index.get_level_values(0))))[window-1:]
beta1 = pd.DataFrame(beta1.T, index=index, columns=ret.columns)
beta2 = pd.DataFrame(beta2.T, index=index, columns=ret.columns)



date_list = get_date_range(20161229, 20191231)
stock_list = get_daily_1factor('common_stock_list', date_list=date_list).sum()
stock_list = stock_list[stock_list >= 1].index.to_list()


beta1 = pd.read_hdf('/data/user/015836/beta1.h5', 'beta1').reindex(index=date_list[1:-1], columns=stock_list)
roll_window = 242 * (boll_day + 1)
beta = np.expand_dims(beta1.T.values, axis=2).repeat(roll_window, axis=2)

ret = get_minute_return(minute_interval=1, start_date=20161229, end_date=20191231).reindex(columns=stock_list)
ret_index = ret.index
ret = np.log(1 + ret).T
ret = ret.values.reshape(ret.shape[0], ret.shape[1] // 242, 242)
ret = _rolling_windows(ret.swapaxes(0, 1), boll_day + 1).swapaxes(1, 2)
ret = ret.reshape(ret.shape[0], ret.shape[1], roll_window).swapaxes(0, 1)

rb = get_minute_1factor('close', 201612281500, 20191231, code_list=[bench], type='bench').pct_change().iloc[1:]
rb = np.log(1 + rb).T
rb = rb.values.reshape(rb.shape[0], rb.shape[1] // 242, 242)
rb = _rolling_windows(rb.swapaxes(0, 1), boll_day + 1).swapaxes(1, 2)
rb = rb.reshape(rb.shape[0], rb.shape[1], roll_window).swapaxes(0, 1)

res = ret - beta * rb
res = ret
res = res.swapaxes(0, 2)
val = np.nancumsum(res, axis=0)

avg = np.apply_along_axis(np.convolve, 0, val, np.ones(boll_day * 242) / (boll_day * 242), 'valid')
std = np.apply_along_axis(np.convolve, 0, val ** 2, np.ones(boll_day * 242), 'valid')
std -= boll_day * 242 * avg ** 2
std /= boll_day * 242 - 1
std **= 0.5
upper = val[-243:] > avg + 2 * std
lower = val[-243:] < avg - 2 * std
upper = (upper[1:] == False) & (upper[:-1] == True)
lower = (lower[1:] == False) & (lower[:-1] == True)
sign = lower * 1 - upper * 1
sign = sign.swapaxes(0, 1).reshape(sign.shape[0] * sign.shape[1], sign.shape[2])

capm = pd.DataFrame(sign, index=ret_index[-sign.shape[0]:], columns=stock_list)
capm.index = [int(x[0] * 10000 + x[1]) for x in capm.index]

ft.evaluate(capm)

aaa = pd.read_hdf('/data/user/015836/capm.h5', 'capm')
aaa = aaa.loc[:202001010000]
beta1 = pd.read_hdf('/data/user/015836/beta1.h5', 'beta1')