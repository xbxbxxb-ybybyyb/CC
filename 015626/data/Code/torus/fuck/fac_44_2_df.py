from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np
import numpy as np
from numba import njit
from utils_zsj import SMA


    
class fac_44_2_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(10 * int(self.freq))
        self.required_columns = ['high', 'low', 'close', 'open']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 0
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
        
        close = data['close'][-roll_win:]
        high = data['high'][-roll_win:]
        low = data['low'][-roll_win:]
        ts_open = data['open'][-roll_win:]
        hclose = data['close'][-21:]
        dclose = data['close'][-coef*2:]
        
        price = (high + low + ts_open + close) / 4
        vma = nanmean_np(price[-roll_win:])
        score1 = nanmean_np(close[-3:]) - vma
        self.score_list.append(score1)
        score = score1 +  nanmean_np(self.score_list[-std_win:])
        co = cross_hub_num_array(data['close'][-63:], 30) + 1
        vol =  nanstd_np(hclose[1:] - hclose[:-1], ddof = 1)
        score_final = score/co/r(vol)
        self.score_final_list.append(score_final)
        cci_score = cci(self.score_final_list[-250:], 120)[-1]
        self.cci_score_list.append(cci_score)
        
        vma_std = rank_data(self.cci_score_list[-ts_pct_win:])
        self.factor_norm_list.append(vma_std)
        
        fac_short = self.factor_norm_list[-int(coef/2):]
        hclose_short = dclose[-int(coef/2):]
        cs = new_corr(fac_short, hclose_short)
        
        fac_long = self.factor_norm_list[-coef * 2:]
        hclose_long = dclose[-coef * 2:]
    
        cl = new_corr(fac_long, hclose_long)

        if (cs < cl) or (cl < 0):
            return 0
        
        return vma_std

        
        
        
    def pre_calculate(self, data):
        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        aaa = 10
        bbb = 40
        ccc = 1
        roll_win = aaa
        std_win = bbb
        ts_pct_win = 300 * ccc
        
        for i in range(2200, -1, -1):
            if i == 0:
                close = data['close'][-roll_win:]
                high = data['high'][-roll_win:]
                low = data['low'][-roll_win:]
                ts_open = data['open'][-roll_win:]
                hclose = data['close'][-21:]
                cclose = data['close'][-63:]

            else:
                close = data['close'][-roll_win - i: -i]
                high = data['high'][-roll_win- i: -i]
                low = data['low'][-roll_win- i: -i]
                ts_open = data['open'][-roll_win- i: -i]
                hclose = data['close'][-21 - i: -i]
                cclose = data['close'][-63 - i: - i]


            price = (high + low + ts_open + close) / 4
            vma = nanmean_np(price[-roll_win:])
            score1 = nanmean_np(close[-3:]) - vma
            self.score_list.append(score1)
            score = score1 +  nanmean_np(self.score_list[-std_win:])
            co = cross_hub_num_array(cclose, 30) + 1
            vol =  nanstd_np(hclose[1:] - hclose[:-1], ddof = 1)
            score_final = score/co/r(vol)
            self.score_final_list.append(score_final)
            if len(self.score_final_list) > 120:
                cci_score = cci(self.score_final_list[-250:], 120)[-1]
                self.cci_score_list.append(cci_score)
            if len(self.cci_score_list) > 10:
                vma_std = rank_data(self.cci_score_list[-ts_pct_win:])
                self.factor_norm_list.append(vma_std)

                

            
        




                
                


        