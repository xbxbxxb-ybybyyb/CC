import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def ts_max(df1, d):
    # time-series max over the past d1 periods ,whose min_periods is d2
    output = pd.DataFrame(bk.move_max(df1, window=d, min_count=int(d/2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


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


class wsc_tsmax_amount(FactorGenerator):
    def __init__(self):
        required_columns = ['amount', 'recent_month_mask']
        lookback_bars = 2000
        super(wsc_tsmax_amount, self).__init__(required_columns=required_columns,
                                               lookback_bars=lookback_bars)

    def on_bar(self, df):
        # 算子搜索
        mask = df['recent_month_mask']
        factor = df['amount']
        factor = ts_max(factor, 45)
        factor = rolling_norm(factor, 120)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor>=0.75] = np.nan
        # factor[(factor<=-0.6)&(factor>=-0.5)] = np.nan
        return factor
