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


class xdy_ts1_future_if(FactorGenerator):
    def __init__(self):
        required_columns = ['high_if', 'close_if', 'recent_month_mask']
        lookback_bars = 2000
        super(xdy_ts1_future_if, self).__init__(required_columns=required_columns,
                                                lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_if']
        close = df['close_if']
        gain_high_60 = high / high.shift(100) - 1
        h_c = close / high - 1
        a = mean(h_c, 60)
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(gain_high_60 / a, 5)
        factor = mean(factor, 10) * -1
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 3 * 242)
        mask = df['recent_month_mask']
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0

        return factor
