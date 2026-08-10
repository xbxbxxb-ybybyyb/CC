from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np



class fac_75_df(FutureFactor):


    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(125 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = ['buy_super_count', 'sell_super_count',  'buy_gigantic_count', 'sell_gigantic_count']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 1200
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.temp2_list = []
        self.temp4_list = []


        
    def calculate(self, data):
        
        fac = (data['buy_super_count'][-125:] - data['sell_super_count'][-125:]+ data['buy_gigantic_count'][-125:] - data['sell_gigantic_count'][-125:]) #/ r((data['volume'].copy()))
        
        fac1 = irr_filter_numba(fac, 25)
        
        return fac1[-1]
        
    def pre_calculate(self, data):
        pass


        
        