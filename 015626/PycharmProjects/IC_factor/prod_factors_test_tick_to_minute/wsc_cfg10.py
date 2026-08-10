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


def ts_sma(df1, alpha):
    # 移动平均 Y_0 = A_0, Y_i = alpha*A_i + (1-alpha)*Y_(i-1)
    output = df1.ewm(alpha=alpha, adjust=False).mean()
    return output
    

class wsc_cfg10(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg10, self).__init__(required_columns=['close_zz500', 'weight_zz500', 'close_spot'],
                                        lookback_bars=2000)

    def on_bar(self, data):
        # factor logic
        close = data['close_zz500']
        ret = close.pct_change(15, fill_method=None)
        # ret_mean = ret.mean(axis=1)
        # ret_std = ret.std(axis=1)
        ret_flag = ret.gt(ret.quantile(0.9, axis=1), axis=0)
        ret_long = ret[ret_flag]
        weight_long = data['weight_zz500'][ret_flag]
        # factor = factor.rolling(10, min_periods=5).mean()
        # factor = factor.sum(axis=1)

        factor = ((ret_long * data['weight_zz500']).sum(axis=1)) / weight_long.sum(axis=1) - data['close_spot'].pct_change(15, fill_method=None)
        # factor = ((ret_long * data['weight_zz500']).sum(axis=1)) / weight_long.sum(axis=1) - (ret * data['weight_zz500']).sum(axis=1)
        factor = factor.rolling(15, min_periods=2).mean()
        factor = factor.to_frame()   
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 300*4)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        #factor[factor<=-0.5] = np.nan
        factor[factor>=0.5] = np.nan
        return factor
