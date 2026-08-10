from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_8_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * freq)
        self.required_columns = [ 'close', 'volume']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 2000
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__

        self.fac_raw_list = []
    
    def calculate(self, data):

        coef = int(int(self.bars_dict[self.ticker]) / int(self.freq))
        unit = int(self.freq)
        
        dclose = data['close'][-coef:]
        dvolume = data['volume'][-coef:]

        chip_dis_1 = chip_dis_raw(dclose, dvolume, int(75 / unit))
        chip_dis_short = chip_dis_raw(dclose, dvolume,  nanmin_np([int(10 / unit), 3]))
        
        
        fac_raw =  (chip_dis_short - chip_dis_1)
        self.fac_raw_list.append(fac_raw)
        
        return -(fac_raw * 2 + self.fac_raw_list[-2])
        
    def pre_calculate(self, data):
        self.fac_raw_list = []
        coef = int(int(self.bars_dict[self.ticker]) / int(self.freq))
        unit = int(self.freq)
        for i in range(3, -1, -1):
            if i == 0:
                dclose = data['close'][-coef - i:]
                dvolume = data['volume'][-coef - i:]

            else:
                dclose = data['close'][-coef - i: -i]
                dvolume = data['volume'][-coef - i: -i]
 

            chip_dis_1 = chip_dis_raw(dclose, dvolume, int(75 / unit))
            chip_dis_short = chip_dis_raw(dclose, dvolume,  nanmin_np([int(10 / unit), 3]))
            
            
            fac_raw =  (chip_dis_short - chip_dis_1)
            self.fac_raw_list.append(fac_raw)



                
                


        