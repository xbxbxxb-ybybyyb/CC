from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class msfac_9_5min_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * freq)
        self.required_columns = [ 'Buy1Price_mean', 'Buy1OrderQty_mean', 'Sell1Price_mean', 'Sell1OrderQty_mean', 'twap']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 3000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.factor_list = []
    
    def calculate(self, data):


        mid = (data['Buy1Price_mean'][-100:] * data['Buy1OrderQty_mean'][-100:] + data['Sell1Price_mean'][-100:] * data['Sell1OrderQty_mean'][-100:]) / r(data['Sell1OrderQty_mean'][-100:] + data['Buy1OrderQty_mean'][-100:]) 

        fac_raw = -(data['twap'][-100:] - mid)
        fac_raw = ema_1(fac_raw, 100, 1 / 16)
        if ('SC' in self.ticker):
            fac_raw = -fac_raw
        return fac_raw
        
    def pre_calculate(self, data):
        pass




                
                


        