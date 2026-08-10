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


class wsc_cfg6(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg6, self).__init__(required_columns=['close_zz500', 'volume_zz500', 'weight_zz500'],
                                       lookback_bars=2000)

    def on_bar(self, data):
        # factor logic
        stk_close = data['close_zz500']
        stk_volume = data['volume_zz500']
        stk_ret = stk_close.pct_change(5, fill_method=None)
        stk_volume_long = stk_volume.gt(stk_volume.quantile(0.9, axis=1), axis=0)
        factor = stk_ret[stk_volume_long]#.rolling(30, min_periods=20).mean()
        # factor = stk_ret.rolling(30*2, min_periods=15).cov(stk_amt)
        factor = (factor * data['weight_zz500']).sum(axis=1)
        factor = factor.rolling(24, min_periods=12).mean()

        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 600)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        factor[factor<=-0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor
