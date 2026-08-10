import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *


# vma_std
class fac_45(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high', 'close', 'open']

        super(fac_45, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc):
        ##### def data #####
        close = data['close']
        high = data['high']
        low = data['low']
        volume = data['volume']

        ##### calc factor #####
        def calc_vwap_sig(close, high, low, volume, roll_win):
            typical = (high + low + close) / 3
            mf = volume * typical
            volume_sum = SUM(volume, roll_win)
            mf_sum = SUM(mf, roll_win)
            vwap_val = mf_sum / volume_sum
            vwap_diff = close - vwap_val
            return vwap_diff

        """vwap_ma"""
        factor_name = 'vwap_ma'
        roll_win = aaa
        ma_win = bbb
        ts_pct_win = ccc * 300
        score_raw = calc_vwap_sig(close, high, low, volume, roll_win)
        score_raw = score_raw.rolling(60, min_periods = 1).mean()
        vwap_ma = ts_rank(score_raw, ts_pct_win)

        ##### format factor #####
        vwap_ma.name = self.__class__.__name__
        factor = pd.DataFrame(vwap_ma)
        # factor[factor<0]=np.nan
        return factor
