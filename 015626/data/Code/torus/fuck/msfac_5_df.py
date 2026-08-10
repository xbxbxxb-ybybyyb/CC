from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class msfac_5_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * freq)
        self.required_columns = [ 'last_n_4_volume', 'last_n_4_ret', 'close', 'open', 'volume']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 1000
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__
        self.factor_list = []
    
    def calculate(self, data):

        ba = data['last_n_4_ret'][-100:]
        bar_diff = (data['close'][-100:] - data['open'][-100:])
        last_10_diff = data['last_n_4_ret'][-100:]
        temp = last_10_diff / r(bar_diff)
        vl = data['last_n_4_volume'][-100:] / r(data['volume'][-100:])
        fac_raw = ema_1(( temp * vl * np.sign(bar_diff)), 100, 1 / 31)

        return fac_raw
        
    def pre_calculate(self, data):
        pass




                
                


        