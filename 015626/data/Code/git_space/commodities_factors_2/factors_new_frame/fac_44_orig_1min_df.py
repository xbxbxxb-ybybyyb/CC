from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np
import numpy as np
from numba import njit
from utils_zsj import SMA



class fac_44_orig_1min_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(3 * int(self.freq))
        self.required_columns = ['high_secmain', 'low_secmain', 'close_secmain', 'open_secmain']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = 1500
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__

        self.score_list = []
        self.score_final_list = []
        self.cci_score_list = []
        self.factor_norm_list = []
    
    def calculate(self, data):

        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        
        aa = 60
        bbb = 240
        ccc = 5
        roll_win = aa
        std_win = int(np.sqrt(bbb))
        
        close = data['close_secmain'][-roll_win:]
        high = data['high_secmain'][-roll_win:]
        low = data['low_secmain'][-roll_win:]
        ts_open = data['open_secmain'][-roll_win:]
        cclose = data['close_secmain'][-243:]
        
        price = (high + low + ts_open + close) / 4
        vma = nanmean_np(price[-roll_win:])
        score = nanmean_np(close[-5:]) - vma
        self.score_list.append(score)
        score_final = nanmean_np(self.score_list[-std_win:])
        
        co = cross_hub_num_array(cclose, 120) / 5 + 1


        return score_final / co

        
        
        
    def pre_calculate(self, data):
        self.score_list = []
        self.score_final_list = []
        self.cci_score_list = []
        self.factor_norm_list = []
        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        
        aa = 60
        bbb = 240
        ccc = 5
        roll_win = aa
        std_win = int(np.sqrt(bbb))
        
        for i in range(500, -1, -1):
            if i == 0:
                close = data['close_secmain'][-roll_win:]
                high = data['high_secmain'][-roll_win:]
                low = data['low_secmain'][-roll_win:]
                ts_open = data['open_secmain'][-roll_win:]


            else:
                close = data['close_secmain'][-roll_win - i: -i]
                high = data['high_secmain'][-roll_win- i: -i]
                low = data['low_secmain'][-roll_win- i: -i]
                ts_open = data['open_secmain'][-roll_win- i: -i]



            price = (high + low + ts_open + close) / 4
            vma = nanmean_np(price[-roll_win:])
            score = nanmean_np(close[-5:]) - vma
            self.score_list.append(score)
