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


def ts_std(df1, d):
    # moving time-series standard deviation over the past d periods
    output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                          index=df1.index, columns=df1.columns)
    return output


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class wsc_search3_if(FactorGenerator):
    def __init__(self):
        super(wsc_search3_if, self).__init__(required_columns=['high_spot'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # 算法搜索
        data = data['high_spot'].to_frame()
        factor = ts_std(data, 75)

        # factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 600 * 2)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
