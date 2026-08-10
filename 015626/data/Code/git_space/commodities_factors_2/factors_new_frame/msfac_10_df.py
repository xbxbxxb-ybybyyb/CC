from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class msfac_10_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * self.freq)
        self.required_columns = [ 'last_n_4_ret', 'AbsPxPath']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 3000
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__
        self.factor_list = []
    

    
    def calculate(self, data):



        mid = (data['last_n_4_ret'][-100:]) / r(data['AbsPxPath'][-100:].copy())
        fac = ema_1(mid, 100, 1/26)
        
        return fac
        
    def pre_calculate(self, data):
        pass
            




                
                


        