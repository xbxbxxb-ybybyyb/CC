import torch
import numpy as np
import pandas as pd
from skimage.util import view_as_windows


def replace_zero(data, threshold=1e-8, x=np.nan):
    assert isinstance(data, (torch.Tensor, pd.Series, pd.DataFrame, np.ndarray, int, float, np.int64,
                             np.float32)), 'the data structure of input is illegal'
    if isinstance(data, torch.Tensor):
        data = data.clone()
        data[abs(data) < threshold] = x
    elif isinstance(data, (pd.Series, pd.DataFrame)):
        data = data.copy()
        data[abs(data) < threshold] = x
    elif isinstance(data, np.ndarray):
        data = data + 0.  # 下述转化对int类型的ndarray无效，因此事先将数据类型转为float
        data = data.copy()
        data[abs(data) < threshold] = x
    else:
        if np.isclose(data, 0, atol=threshold):
            data = x
    return data


def rolling_window_upgrade(data, window):
    # 升级版rolling_window，可以处理二维数组的情况
    if data.ndim not in [1, 2]:
        raise ValueError('input data must be a 1D or 2D array.')
    if data.ndim == 1:
        data_expanding = view_as_windows(data, (window,))
    else:
        data_expanding = view_as_windows(data, (window, 1))[..., 0]
    return data_expanding


def type_convertor(func):
    """
    与operators文件中的算子相配套，用于调整输出的数据格式，使之与输入的数据格式相一致
    """

    def wrapper(*args, **kwargs):
        data = args[0]
        if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
            raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
        output = func(*args, **kwargs)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(output, index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(output, index=data.index, name=data.name)
        return output

    return wrapper


def calc_avg_bars(sig, signal_lims=(-1, 1), layers=4):
    # 对于numpy信号，在对称开平仓模式下，计算单次开平的平均持仓时间
    threshold = max(signal_lims) - 2 * max(signal_lims) / layers
    sig = np.nan_to_num(sig)
    sig[sig > threshold] = threshold
    sig[sig < -threshold] = -threshold
    sig[(sig < threshold) & (sig > -threshold)] = 0
    sig /= threshold
    assert np.all([item in [-1, 0, 1] for item in np.unique(sig)])
    flag = sig[1:] * sig[:-1]
    sig = sig[:-1]
    avg_long_bars = (sig == 1).sum() / ((sig == 1) & (flag != 1)).sum()
    avg_short_bars = (sig == -1).sum() / ((sig == -1) & (flag != 1)).sum()
    return (avg_long_bars + avg_short_bars) / 2
