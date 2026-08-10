from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_ms_4_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * self.freq)
        self.required_columns = [ 'close', 'low']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 600
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.factor_list = []
    

    
    def calculate(self, data):

        dclose =  data['close'][-241:]
        ddiff = dclose[1:] - dclose[:-1]


        localhigh = nanargmin_new(data['low'][-240:]) + 240
        fac = ddiff[localhigh:]
        factor = nanmean_np(fac) / r(nanstd_np(fac))
        
        return factor
        
    def pre_calculate(self, data):
        pass
            




                
                


        