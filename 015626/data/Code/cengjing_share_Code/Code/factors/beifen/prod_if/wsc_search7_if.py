import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def log(df1):
    output = np.log(df1[df1 > 0])
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def ts_decay_linear(df1, d):
    # weighted moving average over the past d periods
    # linearly decaying weights d, d – 1, …, 1 (rescaled to sum up to 1)
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    weight = np.arange(d) + 1
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(weight, (temp_y.shape[0], 1))
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = ((temp_y * temp_x).sum(axis=1) / temp_x.sum(axis=1)) * flag
    return output


class wsc_search7_if(FactorGenerator):
    def __init__(self):
        super(wsc_search7_if, self).__init__(required_columns=['volume', 'recent_month_mask'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # 算法搜索
        mask = data['recent_month_mask']
        data = data['volume']
        factor1 = log(data)
        factor = ts_decay_linear(factor1, 55)
        factor = rolling_norm(factor, 1000)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
