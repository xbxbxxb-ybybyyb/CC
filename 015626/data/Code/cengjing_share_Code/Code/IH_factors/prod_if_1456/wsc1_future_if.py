import pandas as pd
import numpy as np
from factor_generator import FactorGenerator


def log(df):
    return np.log(df[df > 0])


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


class wsc1_future_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_if', 'recent_month_mask']
        lookback_bars = 2000
        super(wsc1_future_if, self).__init__(required_columns=required_columns,
                                              lookback_bars=lookback_bars)

    def on_bar(self, df):
        # 算法搜索
        mask = df['recent_month_mask']
        factor = log(df['close_if'])
        factor = rolling_norm(factor)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= -0.5] = 0
        return factor
