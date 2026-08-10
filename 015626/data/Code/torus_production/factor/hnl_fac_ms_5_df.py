from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_ms_5_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * self.freq)
        self.required_columns = [ 'close', 'high']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 600
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.factor_list = []
    

    
    def calculate(self, data):

        dclose = data['close'][-71:]
        ddiff = dclose[1:] - dclose[:-1]

        localhigh = nanargmax_new(data['high'][-70:]) + 70
        fac = ddiff[localhigh:]
        factor = nanmean_np(fac) / r(nanstd_np(fac))
        if np.isnan(factor):
            factor = self.factor_list[-1]
        self.factor_list.append(factor)
        return factor + irr_filter_raw(self.factor_list[-10:], 2)[-1]
        
    def pre_calculate(self, data):
        for i in range(60, -1, -1):
            if i == 0:
                dclose = data['close'][-71:]
                dhigh = data['high'][-70:]
            else:
                dclose = data['close'][-71 - i: -i]
                dhigh = data['high'][-70 - i: -i]
                
            ddiff = dclose[1:] - dclose[:-1]
            localhigh = nanargmax_new(dhigh) + 70
            fac = ddiff[localhigh:]
            factor = nanmean_np(fac) / r(nanstd_np(fac))
            if np.isnan(factor):
                if len(self.factor_list) != 0:
                    factor = self.factor_list[-1]
                else:
                    pass
            self.factor_list.append(factor)




                
                


        