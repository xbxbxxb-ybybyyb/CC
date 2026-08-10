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


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


class wsc3_future(FactorGenerator):
    def __init__(self):
        super(wsc3_future, self).__init__(required_columns=['close'],
                                                lookback_bars=2000)

    def on_bar(self, data):
        a = data['close'].pct_change(5, fill_method=None)
        b = a.rolling(45, min_periods=15).mean()
        c = a.rolling(45, min_periods=15).std()
        factor = b + 2 * c
        # factor = rolling_norm(a, 240) + rolling_norm(b, 240)
        factor = factor.rolling(10).mean()
        # factor = factor.rolling(60*4, min_periods=30*4).mean()
        # factor = abs(factor - factor.rolling(500, min_periods=250).median())
        # print(factor)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = ts_rank(factor, 600)
        # factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
