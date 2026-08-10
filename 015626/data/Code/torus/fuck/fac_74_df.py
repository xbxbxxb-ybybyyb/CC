from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np



class fac_74_df(FutureFactor):


    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(50/ self.bars_dict[self.ticker])) * freq)
        self.required_columns = ['buy_gigantic_volume', 'sell_gigantic_volume',  'buy_super_volume', 'sell_super_volume']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 1500
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.temp2_list = []
        self.temp4_list = []


        
    def calculate(self, data):
        fac = (data['buy_gigantic_volume'][-60:] - data['sell_gigantic_volume'][-60:] + data['buy_super_volume'][-60:] - data['sell_super_volume'][-60:])
        fac1 = ema_1(fac[-50:], 50, 1/16)
        
        return fac1
        
    def pre_calculate(self, data):
        pass


        
        