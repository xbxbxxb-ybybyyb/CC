from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class msfac_8_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * freq)
        self.required_columns = [ 'PxVolCorr_secmain']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = 3000
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__
        self.factor_list = []
    
    def calculate(self, data):


        ba = data['PxVolCorr_secmain'][-100:]

        fac_raw = ema_1(ba, 100, 1 / 46)


        return fac_raw
        
    def pre_calculate(self, data):
        pass




                
                


        