from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np
import numpy as np
from numba import njit
from utils_zsj import SMA



class fac_59_orig_1min_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(5 * int(freq))
        self.required_columns = [ 'close_secmain']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = 30
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__

        self.close_ma_list = []
        self.dpo_list = []


    
    def calculate(self, data):
        aa = 360
        bb = 360
        ccc = 30
        roll_win = aa
        ma_win = int(np.sqrt(bb))
        ts_pct_win = ccc

        dclose = data['close_secmain'][-roll_win:]
        
        close_ma = nanmean_np(dclose[-roll_win:])
        self.close_ma_list.append(close_ma)
        dpo = dclose[-1] - self.close_ma_list[-int(roll_win / 2 + 1)-1]
        self.dpo_list.append(dpo)
        fac= ema_1(self.dpo_list[-ma_win * 3:], ma_win * 3, 1 / (ma_win + 1))
        return fac


    
    def pre_calculate(self, data):
        self.close_ma_list = []
        self.dpo_list = []
        aa = 360
        bb = 360
        ccc = 30
        roll_win = aa
        ma_win = int(np.sqrt(bb))
        ts_pct_win = ccc
        for i in range(400, -1, -1):
            if i == 0:
                dclose = data['close_secmain'][-roll_win:]
            else:
                dclose = data['close_secmain'][-roll_win - i: -i]
        
            close_ma = nanmean_np(dclose[-roll_win:])
            self.close_ma_list.append(close_ma)
            if len(self.close_ma_list) > 181:
                if len(dclose) == 0:
                    if len(self.close_ma_list) > 1:
                        dpo = self.close_ma_list[-1]
                    else:
                        dpo = np.nan
                else:
                    dpo = dclose[-1] - self.close_ma_list[-int(roll_win / 2 + 1)-1]
                self.dpo_list.append(dpo)