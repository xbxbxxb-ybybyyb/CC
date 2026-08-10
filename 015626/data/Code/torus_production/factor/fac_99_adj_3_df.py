from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_99_adj_3_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(1501 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [  'close', 'BidAskSpreadMean',  'buy_active', 'sell_active', 'buy_gigantic_volume', 'sell_gigantic_volume']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 2400
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.fac_list = []

    def calculate(self, data):
        if ('czc' in self.ticker.lower()) or ('zce' in self.ticker.lower()):
            return 0
            
        hclose = data['close'][-31:]
        coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(data['BidAskSpreadMean'][-30:]))


        aaa = 300
        
        if coef_temp > 10:
            coef =0.1
        elif (coef_temp > 6) and (coef_temp <= 10):
            coef = 0.5
        elif (coef_temp > 4) and (coef_temp <= 6):
            coef = 1
        elif (coef_temp > 3) and (coef_temp <= 4):
            coef = 3
        elif (coef_temp <= 3):
            coef = 5
        else:
            coef = 6

        close_diff = data['buy_gigantic_volume'][-1501:] + data['sell_gigantic_volume'][-1501:]
        locallow = nanargmax_new(close_diff[-int(nanmax_np([1, aaa * coef])):]) 

        fac = data['buy_active'][-900:] - data['sell_active'][-900:]
        
        fac1 = nanmean_np(fac[locallow:])

        return fac1
    def pre_calculate(self, data):
        pass

        