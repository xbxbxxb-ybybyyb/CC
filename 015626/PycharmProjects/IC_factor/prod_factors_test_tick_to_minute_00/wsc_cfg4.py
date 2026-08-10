import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex


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


class wsc_cfg4(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg4, self).__init__(required_columns=['close_zz500', 'open_zz500', 'weight_zz500', 'high_zz500', 'low_zz500'],
                                       lookback_bars=2000)

    def on_bar(self, data):
        # factor logic
        a = data['high_zz500'] - data['low_zz500']
        a[abs(a)<1e-8] = np.nan
        b = (data['close_zz500']-data['open_zz500'])
        b[b<0] = np.nan
        c = (b/a).rolling(30*2, min_periods=10).sum()
        factor = (c * data['weight_zz500']).sum(axis=1)
        #factor = factor.rolling(5, min_periods=1).mean()
        factor = factor.rolling(5, min_periods=2).mean()

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = ts_rank(factor, 200*6)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor
