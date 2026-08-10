import pandas as pd
import numpy as np
import warnings
import bottleneck as bk
from collections import deque


def ts_median_winsorize(pd_raw, ma_window, dev_window, outlier_distance=5):
    if isinstance(pd_raw, pd.Series) or isinstance(pd_raw, np.ndarray):
        np_data = pd.DataFrame(pd_raw).values
    elif isinstance(pd_raw, pd.DataFrame):
        np_data = pd_raw.values.copy()
    else:
        raise AssertionError
    np_data[~np.isfinite(np_data)] = np.nan
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        np_median = bk.move_median(np_data, window=ma_window, min_count=int(ma_window / 2), axis=0)
        np_dev = np_data - np_median
        np_dev_median = bk.move_median(np.abs(np_dev), window=dev_window, min_count=int(dev_window / 2), axis=0)
        np_env_top = np_median + outlier_distance * np_dev_median
        np_env_bot = np_median - outlier_distance * np_dev_median
        res = np_data
        res = np.where(res < np_env_top, res, np_env_top)
        res = np.where(res > np_env_bot, res, np_env_bot)
        # pad result nan with original
        res = np.where(np.isnan(res), np_data, res)
        # drop original nan within result
        res = np.where(np.isnan(np_data), np_data, res)
    if isinstance(pd_raw, pd.Series):
        res = pd.Series(res.ravel(), index=pd_raw.index)
        res.index.name = pd_raw.index.name
        res.name = pd_raw.name
    elif isinstance(pd_raw, np.ndarray):
        res = np.reshape(res, pd_raw.shape)
    else:
        res = pd.DataFrame(res, columns=pd_raw.columns, index=pd_raw.index)
    return res


def ts_ma_winsorize(x, ma_window, dev_window, outlier_distance=5):
    # look back periods equal ma + dev windows
    if isinstance(x, np.ndarray):
        assert len(x.shape) == 1
        _x = x.copy()
    elif isinstance(x, pd.Series):
        _x = x.values.copy()
    else:
        raise NotImplementedError
    _x[~np.isfinite(_x)] = np.nan
    ma = None
    dev = None
    ma_queue = deque(maxlen=ma_window)
    dev_queue = deque(maxlen=dev_window)
    for i in np.nditer(_x, op_flags=['readwrite']):
        if np.isnan(i):
            continue
        if ma is not None:
            _dev = abs(i - ma)
            if dev is not None and dev !=0 and _dev / dev >= outlier_distance:
                if i > ma:
                    i[...] = ma + outlier_distance * dev
                else:
                    i[...] = ma - outlier_distance * dev
                _dev = abs(i - ma)
            dev_queue.append(_dev)
        ma_queue.append(i)
        # update moving average and deviation
        if len(ma_queue) == ma_window:
            ma = np.mean(ma_queue)
        if len(dev_queue) == dev_window:
            dev = np.mean(dev_queue)
    if isinstance(x, pd.Series):
        _x = pd.Series(_x, index=x.index)
        _x.index.name = x.index.name
        _x.name = x.name
    return _x

