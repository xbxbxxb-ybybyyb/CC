from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_98_adj_s_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(1816 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [  'close', 'BidAskSpreadMean',  'buy_small_volume', 'sell_small_volume']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 1200
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.fac_list = []

    def calculate(self, data):

        hclose = data['close'][-31:]
        coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(data['BidAskSpreadMean'][-30:]))
        dclose = data['close'][-916:]

        aaa = 300
        
        if coef_temp > 10:
            coef =0.3
        elif (coef_temp > 6) and (coef_temp <= 10):
            coef = 0.5
        elif (coef_temp > 4) and (coef_temp <= 6):
            coef = 1
        elif (coef_temp > 3) and (coef_temp <= 4):
            coef = 2
        elif (coef_temp <= 3):
            coef = 3
        else:
            coef = 6

        close_diff = dclose[15:] - dclose[:-15]
        locallow = nanargmin_new(close_diff[-int(nanmax_np([1, aaa * coef])):]) 

        fac = data['buy_small_volume'][-901:] - data['sell_small_volume'][-901:]
        
        fac1 = nanmean_np(fac[locallow:])
        if ('SC' in self.ticker) or ('AU' in self.ticker) or ('CU' in self.ticker) or ('SN' in self.ticker):
            fac1 = -fac1
        return -fac1
    def pre_calculate(self, data):
        pass

        