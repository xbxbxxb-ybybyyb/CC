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


class wsc_ma1_if(FactorGenerator):
    def __init__(self):
        super(wsc_ma1_if, self).__init__(required_columns=['close_if', 'recent_month_mask'],
                                         lookback_bars=2000)

    def on_bar(self, data):
        # 计算长周期和短周期两条均线，作差表示这两条均线包围的面积
        close = data['close_if']
        mask = data['recent_month_mask']
        close_ma_long = close.rolling(120, min_periods=60).mean()
        close_ma_short = close.rolling(15, min_periods=5).mean()
        factor = close_ma_short - close_ma_long
        factor = rolling_norm(factor, 360)
        factor = factor[mask].sum(axis=1)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
