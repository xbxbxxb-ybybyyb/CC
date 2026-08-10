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


class wyc_ts19_future_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_if', 'low_if', 'high_if', 'volume_if', 'recent_month_mask']
        lookback_bars = 2000
        super(wyc_ts19_future_if, self).__init__(
            required_columns=required_columns,
            lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        a = (df['high_if']- df['low_if'])
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum((((df['close_if'] - df['low_if']) - (df['high_if'] - df['close_if'])) / a * df['volume_if']), 20)
        factor = ts_rank(factor, 240)
        factor = ts_mean(factor, 120)
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 1200)
        factor = factor[mask].sum(axis=1).to_frame()

        factor.columns = [columnname]
        factor[factor <= -0.5] = 0

        return factor
