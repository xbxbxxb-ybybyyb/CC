from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np
import numpy as np
from numba import njit
from utils_zsj import SMA


class fac_45_2_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(20 * int(self.freq))
        self.required_columns = [ 'close', 'volume']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 0
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__

        self.vwap_diff_list = []
        self.fac_raw_list = []
        self.fac_norm_list = []

    
    def calculate(self, data):

        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        aaa = 180
        bbb = 5
        ccc = 5
        ts_pct_win = ccc * 300
        roll_win = aaa
        ma_win = bbb

        
        close = data['close'][-roll_win:]
        volume = data['volume'][-roll_win:]
        cclose = data['close'][-63:]
        dclose = data['close'][-5 * coef:]

        
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
        self.fac_raw_list.append(fac_raw)
        vwap_ma = rank_data(self.fac_raw_list[-ts_pct_win:])
        self.fac_norm_list.append(vwap_ma)
        
        fac_short = self.fac_norm_list[-int(coef):]
        hclose_short = dclose[-int(coef):]
        cs = new_corr(fac_short, hclose_short)
        
        fac_long = self.fac_norm_list[-coef * 5:]
        hclose_long = dclose[-coef * 5:]
    
        cl = new_corr(fac_long, hclose_long)
        if (cs < cl) or (cl < 0):
            return 0
        return vwap_ma

        
        
        
    def pre_calculate(self, data):
        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        
        aaa = 180
        bbb = 5
        ccc = 5
        ts_pct_win = ccc * 300
        roll_win = aaa
        ma_win = bbb
        
        for i in range(4400, -1, -1):
            if i == 0:
                close = data['close'][-roll_win:]
                volume = data['volume'][-roll_win:]
                cclose = data['close'][-63:]
                dclose = data['close'][-5 * coef:]


            else:
                close = data['close'][-roll_win - i: -i]
                volume = data['volume'][-roll_win - i: -i]
                cclose = data['close'][-63 - i: -i]
                dclose = data['close'][-5 * coef - i: -i]


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
                score_raw = nanmean_np(self.vwap_diff_list[-ma_win:])
                co = cross_hub_num_array(cclose, 30) / 5 + 1
                fac_raw = score_raw / r(co)
                self.fac_raw_list.append(fac_raw)
                vwap_ma = rank_data(self.fac_raw_list[-ts_pct_win:])
                self.fac_norm_list.append(vwap_ma)
            
