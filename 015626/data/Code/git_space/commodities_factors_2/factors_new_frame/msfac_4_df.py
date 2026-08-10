from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class msfac_4_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * freq)
        self.required_columns = [ 'last_n_4_volume_secmain', 'last_n_4_ret_secmain', 'close_secmain', 'open_secmain']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = 4500
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__
        self.factor_list = []
    
    def calculate(self, data):


        ba = data['last_n_4_ret_secmain'][-200:]
        bar_diff = (data['close_secmain'] - data['open_secmain'])[-200:]
        last_10_diff = data['last_n_4_ret_secmain'][-200:]
        temp = last_10_diff / r(bar_diff)
        fac_mid = (temp * np.sign(bar_diff))
        fac = ema_1(fac_mid, 200, 1 / 41)
        return fac
        
    def pre_calculate(self, data):
        pass




                
                


        