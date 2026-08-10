from factor_generator import FactorGenerator
# from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk


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


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def ts_mean(df1, d):
    # moving time-series average for the past d periods
    output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class wyc_ts29_icfuture_if(FactorGenerator):
    def __init__(self):
        lookback_bars = 2000
        required_columns = ['close', 'volume', 'recent_month_mask']
        super(wyc_ts29_icfuture_if, self).__init__(
            required_columns=required_columns,
            lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        N = 20
        factor = (df['close'] - delay(df['close'], N)) / delay(df['close'], N) * df['volume']
        factor = ts_rank(factor, 300)
        factor = ts_mean(factor, 20)
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1).to_frame()

        factor.columns = [columnname]
        factor[factor <= -0.5] = 0

        return factor
