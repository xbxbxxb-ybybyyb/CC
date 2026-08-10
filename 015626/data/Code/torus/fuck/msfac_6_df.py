from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class msfac_6_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * freq)
        self.required_columns = [ 'Buy1OrderQty_mean', 'Sell1OrderQty_mean']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 3000
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__
        self.factor_list = []
    
    def calculate(self, data):

        ba = data['Buy1OrderQty_mean'][-100:]
        sa = data['Sell1OrderQty_mean'][-100:]
        fac_raw = -((ba - sa) / r(ba + sa))
        fac_raw = ema_1(fac_raw, 100, 1 / 9)

        return fac_raw
        
    def pre_calculate(self, data):
        pass




                
                


        