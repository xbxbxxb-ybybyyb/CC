from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_6_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(2 * freq)
        self.required_columns = [ 'close', 'volume']
        self.instrument_type = 'main' #second_main
        self.normalize_size = int(int(self.bars_dict[self.ticker]) * 10)
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__

        self.chip_dis_short_list = []
    
    def calculate(self, data):

        coef = int(int(self.bars_dict[self.ticker]) / int(self.freq))
        
        dclose = data['close'][-coef * 2:]
        dvolume = data['volume'][-coef * 2:]

        chip_dis_1 = chip_dis_raw(dclose, dvolume, coef * 1)
        chip_dis_short = chip_dis_raw(dclose, dvolume,  3)
        self.chip_dis_short_list.append(chip_dis_short)
        
        fac = (chip_dis_short - nanmean_np(self.chip_dis_short_list[-25:])) - chip_dis_1
        
        
        return -fac
        
    def pre_calculate(self, data):
        coef = int(int(self.bars_dict[self.ticker]) / int(self.freq))
        for i in range(26, -1, -1):
            if i == 0:
                dclose = data['close'][-coef * 2 - i:]
                dvolume = data['volume'][-coef * 2 - i:]

            else:
                dclose = data['close'][-coef * 2 - i: -i]
                dvolume = data['volume'][-coef * 2 - i: -i]
 

            chip_dis_short = chip_dis_raw(dclose, dvolume,  3)
            self.chip_dis_short_list.append(chip_dis_short)



                
                


        