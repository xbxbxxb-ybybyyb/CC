import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from operators_all_wsc import cross_hub_num
from utils_zsj import *

# VMA_STD
def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))


# vma_std
class fac_58_orig_1min_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'low', 'second_main_mask', 'high', 'volume']

        super(fac_58_orig_1min_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):
        aa = 30
        bb = 300
        ccc = 1

        ##### def data #####
        close = data['close']
        high = data['high']
        low = data['low']
        volume = data['volume']
        mask = data['second_main_mask']
        ##### calc factor #####
        def calc_vwap_sig(close, high, low, volume, roll_win, mask):
            typical = close
            mf = volume * typical
            volume_sum = SUM(volume, roll_win)
            mf_sum = SUM(mf, roll_win)
            vwap_val = mf_sum / r(volume_sum)
            vwap_diff = close - vwap_val
            return vwap_diff[mask].mean(axis = 1)

        """vwap_ma"""
        factor_name = 'vwap_ma'
        roll_win = aa
        ma_win = int(np.sqrt(bb))
        
        score_raw1 = calc_vwap_sig(close, high, low, volume, roll_win, mask)
        score_raw1 = score_raw1.rolling(ma_win, min_periods = 1).mean()
        coef = int(np.nanmedian(mask.groupby(mask.index.date).count()))
        ts_pct_win = ccc * coef
        #score_raw2 = calc_vwap_sig(close, high, low, volume, 240, mask)
        #score_raw = (score_raw2).rolling(ma_win, min_periods = 1).mean()
        
        co = (cross_hub_num(data['close'], 30)[mask].mean(axis = 1) / 5) + 1
        vwap_ma = ts_rank(score_raw1 / r(co), ts_pct_win)
        
        ##### format factor #####
        vwap_ma.name = self.__class__.__name__
        factor = pd.DataFrame(vwap_ma)
        # factor[factor<0]=np.nan
        return factor