import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *
from operators_all_wsc import cross_hub_num

# vma_std
class fac_45_orig_1min_df(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high', 'close', 'volume', 'second_main_mask']

        super(fac_45_orig_1min_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc):
        aaa = 240
        bbb = 240
        ccc = 20
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
        roll_win = aaa
        ma_win = int(np.sqrt(bbb))
        ts_pct_win = ccc * 300
        #score_raw1 = calc_vwap_sig(close, high, low, volume, roll_win, mask)
        #score_raw1 = score_raw1.rolling(ma_win, min_periods = 1).mean()
        
        score_raw2 = calc_vwap_sig(close, high, low, volume, 240, mask)
        score_raw = (score_raw2).rolling(ma_win, min_periods = 1).mean()
        
        co = (cross_hub_num(data['close'], 30)[mask].mean(axis = 1) / 5) + 1
        vwap_ma = ts_rank(score_raw / r(co), ts_pct_win)
        
        ##### format factor #####
        vwap_ma.name = self.__class__.__name__
        factor = pd.DataFrame(vwap_ma)
        # factor[factor<0]=np.nan
        return factor

