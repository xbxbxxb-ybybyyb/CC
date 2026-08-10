from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np
import numpy as np
from numba import njit
from utils_zsj import SMA


class fac_45_orig_1min_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(2 * int(self.freq))
        self.required_columns = [ 'close_secmain', 'volume_secmain']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = 6000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__

        self.vwap_diff_list = []
        self.fac_raw_list = []
        self.fac_norm_list = []

    
    def calculate(self, data):

        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        aaa = 240
        bbb = 240
        ccc = 20
        ts_pct_win = ccc * 300
        roll_win = aaa
        ma_win = int(np.sqrt(bbb))

        
        close = data['close_secmain'][-roll_win:]
        volume = data['volume_secmain'][-roll_win:]
        cclose = data['close_secmain'][-63:]

        
        typical = close
        mf = volume * typical
        volume_sum = nansum_np(volume[-roll_win:])
        mf_sum = nansum_np(mf[-roll_win:])
        vwap_val = mf_sum / r(volume_sum)
        vwap_diff = close[-1] - vwap_val
        self.vwap_diff_list.append(vwap_diff)
        score_raw = nanmean_np(self.vwap_diff_list[-ma_win:])
        co = cross_hub_num_array(cclose, 30) / 5 + 1
        fac_raw = score_raw / r(co)

        return fac_raw

        
        
        
    def pre_calculate(self, data):
        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        
        aaa = 240
        bbb = 240
        ccc = 20
        ts_pct_win = ccc * 300
        roll_win = aaa
        ma_win = int(np.sqrt(bbb))
        
        for i in range(300, -1, -1):
            if i == 0:
                close = data['close_secmain'][-roll_win:]
                volume = data['volume_secmain'][-roll_win:]
                cclose = data['close_secmain'][-63:]
                dclose = data['close_secmain'][-5 * coef:]


            else:
                close = data['close_secmain'][-roll_win - i: -i]
                volume = data['volume_secmain'][-roll_win - i: -i]
                cclose = data['close_secmain'][-63 - i: -i]
                dclose = data['close_secmain'][-5 * coef - i: -i]


            if len(close) == 0:
                self.vwap_diff_list.append(np.nan)
            else:
                typical = close
                mf = volume * typical
                volume_sum = nansum_np(volume[-roll_win:])
                mf_sum = nansum_np(mf[-roll_win:])
                vwap_val = mf_sum / r(volume_sum)
                vwap_diff = close[-1] - vwap_val
                self.vwap_diff_list.append(vwap_diff)
            
