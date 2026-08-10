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
    

class wsc_cfg9(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg9, self).__init__(required_columns=['close_zz500', 'weight_zz500', 'high_zz500', 'low_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # factor logic
        close = data['close_zz500']
        high = data['high_zz500']
        low = data['low_zz500']
        N = 30
        bull_power = high - ts_sma(close, alpha=(N-1)/(N+1))
        bear_power = low - ts_sma(close, alpha=(N-1)/(N+1))
        factor = bull_power + bear_power
        #dpo =  abs(dpo - dpo.rolling(60, min_periods=30).median())
        # stk_turnover = data['turnover_zz500']#.rolling(2, min_periods=1).mean()
        # a[a<0] = 0
        #a[a>0] = 1
        #factor = stk_volume[stk_vol_long]#.rolling(30, min_periods=20).mean()
        # factor = stk_ret.rolling(30*2, min_periods=15).cov(stk_amt)
        factor = (factor * data['weight_zz500']).sum(axis=1)
        factor = -factor.rolling(65, min_periods=15).mean()

        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = rolling_norm(factor, 300*4)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        #factor[factor<=-0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor
