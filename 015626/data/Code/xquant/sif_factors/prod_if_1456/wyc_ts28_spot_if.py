from factor_generator import FactorGenerator
# from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk


def ts_mean(df1, d):
    # moving time-series average for the past d periods
    output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def ts_sum(df1, d):
    # moving time-series average for the past d periods
    output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def delay(df1, d):
    # A_(i-d)
    output = df1.shift(periods=d)
    return output


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


class wyc_ts28_spot_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_spot_if']
        lookback_bars = 2000
        super(wyc_ts28_spot_if, self).__init__(
            required_columns=required_columns,
            lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        M = 20
        con1 = df['close_spot_if'] > delay(df['close_spot_if'], 10)
        factor = ts_sum(con1.to_frame(), M) / M * 100
        factor = ts_mean(factor, 55)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        # factor[factor <= -0.5] = 0

        return factor
