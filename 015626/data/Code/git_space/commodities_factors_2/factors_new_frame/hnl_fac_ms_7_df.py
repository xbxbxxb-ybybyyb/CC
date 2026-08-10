from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_ms_7_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * self.freq)
        self.required_columns = [ 'last_to_mid', 'high']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 300
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.factor_list = []
    

    
    def calculate(self, data):

        dclose = dclose = data['last_to_mid'][-150:]


        localhigh = nanargmax_new(data['high'][-150:]) + 150
        fac = dclose[localhigh:]
        factor = nanmean_np(fac) / r(nanstd_np(fac))
        
        return -factor
        
    def pre_calculate(self, data):
        pass
            




                
                


        