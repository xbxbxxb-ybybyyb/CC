
import numpy as np
import pandas as pd
from skimage.util import view_as_windows


def rolling_window_upgrade(data, window):
    # 升级版rolling_window，可以处理二维数组的情况
    if data.ndim not in [1, 2]:
        raise ValueError('input data must be a 1D or 2D array.')
    if data.ndim == 1:
        data_expanding = view_as_windows(data, (window,))
    elif data.ndim == 2:
        data_expanding = view_as_windows(data, (window, 1))[..., 0]
    return data_expanding

def irr_filter(input_signal, window):
    alpha = 2 / (window + 1)
    b0 = alpha - (alpha ** 2) / 4
    b1 = (alpha ** 2) / 2
    b2 = -(alpha - (3 * alpha ** 2) / 4)
    a1 = -2 * (1 - alpha)
    a2 = (1 - alpha) ** 2
    y = np.zeros_like(input_signal)
    for n in range(len(input_signal)):
        if n == 0:
            y[n] = b0 * input_signal[n]
        elif n == 1:
            y[n] = b0 * input_signal[n] + b1 * input_signal[n-1] - a1 * y[n-1]
        else:
            y[n] = (b0 * input_signal[n] + b1 * input_signal[n-1] + b2 * input_signal[n-2] - a1 * y[n-1] - a2 * y[n-2])
    return y



def irr_ma(factor, window):
    assert type(factor) == pd.Series
    jd = window * 5
    rw = rolling_window_upgrade(factor.ffill().values, jd)
    factor = pd.Series([np.nan] * (jd - 1) + [irr_filter(item, window)[-1] for item in rw], index = factor.index)
    return factor


