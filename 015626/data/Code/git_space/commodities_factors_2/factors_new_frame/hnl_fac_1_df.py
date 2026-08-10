from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_1_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(2800 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [ 'close', 'volume']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 3000
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__

        self.cd5_list = []
    
    def calculate(self, data):

        coef = int(int(self.bars_dict[self.ticker]) / int(self.freq))
        
        dclose = data['close'][-coef * 5:]
        dvolume = data['volume'][-coef * 5:]

        cd5 = chip_dis_raw(dclose, dvolume, coef * 5)

        self.cd5_list.append(cd5)

        fac1 = nanmean_np(self.cd5_list[-3:]) / nanmean_np(self.cd5_list[-20:])
        return fac1
        
    def pre_calculate(self, data):
        self.cd5_list = []
        coef = int(int(self.bars_dict[self.ticker]) / int(self.freq))
        for i in range(30, -1, -1):
            if i == 0:
                dclose = data['close'][-coef * 5 - i:]
                dvolume = data['volume'][-coef * 5 - i:]

            else:
                dclose = data['close'][-coef * 5 - i: -i]
                dvolume = data['volume'][-coef * 5 - i: -i]
 
            cd5 = chip_dis_raw(dclose, dvolume, coef * 5)

            self.cd5_list.append(cd5)

                
                


        