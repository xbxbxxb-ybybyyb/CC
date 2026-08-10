from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np


def rolling_normalize(sig, window=240, method='max_min'):
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


def ts_position(x, t):
    def get_position(ylist):
        smin = min(ylist)
        smax = max(ylist)
        y = ylist[-1]
        return (y - smin) / (smax - smin)

    return x.rolling(t, min_periods=t // 2).apply(get_position)


class xdy_ts4_future_if(FactorGenerator):
    def __init__(self):
        required_columns = ['high_if', 'recent_month_mask']
        lookback_bars = 2000
        super(xdy_ts4_future_if, self).__init__(required_columns=required_columns,
                                                lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_if']
        factor = ts_position(high, 7)
        factor = -1 * factor.rolling(75, min_periods=20).skew()
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        mask = df['recent_month_mask']
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        # factor.loc[factor[columnname] <= -0.5] = 0

        return factor
