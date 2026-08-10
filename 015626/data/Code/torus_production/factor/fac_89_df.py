from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_89_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * self.freq)
        self.required_columns = ['sell_gigantic_count_secmain',  'buy_gigantic_count_secmain', 'close']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = 2000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.input_signal_list = []
        self.y_list = []
        self.fuck_list = []


        
    def calculate(self, data):


        aaa = 30
        
        bs = data['sell_gigantic_count_secmain'][-aaa:] + data['buy_gigantic_count_secmain'][-aaa:]
        vol = nansum_np(bs)
        up = nansum_np(bs * data['close'][-aaa:]) / r(vol)
        down = r(nanmean_np(bs))
            
        fac1 = up / down


        return fac1
        
    def pre_calculate(self, data):
        pass
            
        




                
                


        