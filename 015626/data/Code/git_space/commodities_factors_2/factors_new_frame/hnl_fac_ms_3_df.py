from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_ms_3_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * freq)
        self.required_columns = [ 'last_to_mid']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 600
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.fac_raw_list = []
        self.fac_list = []
    

    
    def calculate(self, data):



        fac = data['last_to_mid'][-150:]


        factor = irr_filter_raw(fac, 30)[-1]
        if ('SC' in self.ticker) :
            factor = -factor
        return -factor
        
    def pre_calculate(self, data):
        pass




                
                


        