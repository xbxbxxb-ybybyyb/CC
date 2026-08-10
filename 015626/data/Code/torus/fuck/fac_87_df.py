from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_87_df(FutureFactor):


    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * self.freq)
        self.required_columns = ['buy_gigantic_volume',  'sell_gigantic_volume', 'close']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 2000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.input_signal_list = []
        self.y_list = []
        self.fuck_list = []


        
    def calculate(self, data):
        if ('czc' in self.ticker.lower()) or ('zce' in self.ticker.lower()):
            return 0

        aaa = 200
        
        bs = data['sell_gigantic_volume'][-aaa:] + data['buy_gigantic_volume'][-aaa:]
        vol = nansum_np(bs)
        up = nansum_np(bs * data['close'][-aaa:]) / r(vol)
        down = r(nanmean_np(bs))
            
        fac1 = up / down


        return fac1
        
    def pre_calculate(self, data):
        pass
        
        