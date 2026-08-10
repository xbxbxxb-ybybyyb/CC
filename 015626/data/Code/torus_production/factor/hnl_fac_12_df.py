from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_12_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(600 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [ 'close', 'volume']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 600
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__

        self.fac_raw_list = []
    
    def calculate(self, data):

        dclose = data['close'][-555:]
        dvolume = data['volume'][-555:]
        unit = int(self.freq)        
        coef = int(int(self.bars_dict[self.ticker]) / int(self.freq))
        

        window1 = nanmax_np([5, int(10/unit)])
        cd_short = chip_dis_raw(dclose, dvolume, window1) - 0.5
        cd5 = chip_dis_raw(dclose, dvolume, coef) - 0.5
        fac_raw = cd_short * cd5 * cd5
        self.fac_raw_list.append(fac_raw)

        fac1 = ema_1(self.fac_raw_list[-35:], 35, 1 /6)
        return fac1
        
    def pre_calculate(self, data):
        for i in range(40, -1, -1):
            if i == 0:
                dclose = data['close'][-555 - i:]
                dvolume = data['volume'][-555 - i:]

            else:
                dclose = data['close'][-555 - i: -i]
                dvolume = data['volume'][-555 - i: -i]
 
            unit = int(self.freq)        
            coef = int(int(self.bars_dict[self.ticker]) / int(self.freq))
            
    
            window1 = nanmax_np([5, int(10/unit)])
            cd_short = chip_dis_raw(dclose, dvolume, window1) - 0.5
            cd5 = chip_dis_raw(dclose, dvolume, coef) - 0.5
            fac_raw = cd_short * cd5 * cd5
            self.fac_raw_list.append(fac_raw)
                


        