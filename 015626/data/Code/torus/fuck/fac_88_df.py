from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_88_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * self.freq)
        self.required_columns = ['sell_active_secmain',  'buy_active_secmain', 'close_secmain']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = 1200
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.input_signal_list = []
        self.y_list = []
        self.fuck_list = []


        
    def calculate(self, data):


        aaa = 30
        
        bs = data['sell_active_secmain'][-aaa:] + data['buy_active_secmain'][-aaa:]
        vol = nansum_np(bs)
        up = nansum_np(bs * data['close_secmain'][-aaa:]) / r(vol)
        down = r(nanmean_np(bs))
            
        fac1 = up / down


        return fac1
        
    def pre_calculate(self, data):
        pass




                
                


        