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


class wsc_cfg7_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg7_if, self).__init__(required_columns=['close_hs300', 'weight_hs300', 'amount_hs300', 'weight_boolean_hs300'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # factor logic
        bool_mask = data['weight_boolean_hs300']
        stk_close = data['close_hs300']
        stk_amt = data['amount_hs300'][bool_mask]
        stk_ret = stk_close.pct_change(3, fill_method=None)[bool_mask]
        stk_ret_long = stk_ret.gt(stk_ret.quantile(0.8, axis=1), axis=0)
        factor = stk_amt[stk_ret_long]
        factor = (factor * data['weight_hs300']).sum(axis=1)
        factor = factor.rolling(20, min_periods=7).mean()

        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 200*6)
        factor[factor<=-0.5] = 0
        #factor[factor>=0.5] = np.nan
        return factor
