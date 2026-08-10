from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np
import numpy as np
from numba import njit
from utils_zsj import SMA



class fac_44_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(4 * int(self.freq))
        self.required_columns = ['high_secmain', 'low_secmain', 'close_secmain', 'open_secmain']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = 300
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__

        self.score_list = []
        self.score_final_list = []
        self.cci_score_list = []
        self.factor_norm_list = []
    
    def calculate(self, data):

        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        
        aaa = 10
        bbb = 40
        ccc = 1
        roll_win = aaa
        std_win = bbb
        ts_pct_win = 300 * ccc
        
        close = data['close_secmain'][-roll_win:]
        high = data['high_secmain'][-roll_win:]
        low = data['low_secmain'][-roll_win:]
        ts_open = data['open_secmain'][-roll_win:]
        hclose = data['close_secmain'][-21:]
        cclose = data['close_secmain'][-63:]
        
        price = (high + low + ts_open + close) / 4
        vma = nanmean_np(price[-roll_win:])
        score = nanmean_np(close[-3:]) - vma
        self.score_list.append(score)
        score_final = score + nanmean_np(self.score_list[-std_win:])
        self.score_final_list.append(score_final)
        co = cross_hub_num_array(cclose, 30) + 1
        vol =  nanstd_np(hclose[1:] - hclose[:-1], ddof = 1)
        cci_score = cci(self.score_final_list[-250:], 120)[-1]

        return cci_score / co /r(vol)

        
        
        
    def pre_calculate(self, data):
        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        aaa = 10
        bbb = 40
        ccc = 1
        roll_win = aaa
        std_win = bbb
        ts_pct_win = 300 * ccc
        
        for i in range(1200, -1, -1):
            if i == 0:
                close = data['close_secmain'][-roll_win:]
                high = data['high_secmain'][-roll_win:]
                low = data['low_secmain'][-roll_win:]
                ts_open = data['open_secmain'][-roll_win:]
                hclose = data['close_secmain'][-21:]
                cclose = data['close_secmain'][-63:]

            else:
                close = data['close_secmain'][-roll_win - i: -i]
                high = data['high_secmain'][-roll_win- i: -i]
                low = data['low_secmain'][-roll_win- i: -i]
                ts_open = data['open_secmain'][-roll_win- i: -i]
                hclose = data['close_secmain'][-21 - i: -i]
                cclose = data['close_secmain'][-63 - i: - i]


            price = (high + low + ts_open + close) / 4
            vma = nanmean_np(price[-roll_win:])
            score = nanmean_np(close[-3:]) - vma
            self.score_list.append(score)
            score_final = score + nanmean_np(self.score_list[-std_win:])
            self.score_final_list.append(score_final)
