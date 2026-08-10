from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_91_adj_2_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(901 / self.bars_dict[self.ticker])) * self.freq)
        self.required_columns = ['last_to_mid', 'high', 'BidAskSpreadMean', 'close']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 1200
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__


    def calculate(self, data):
        hclose = data['close'][-31:]
        coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(data['BidAskSpreadMean'][-30:]))
        
        aaa = 150
        
        if coef_temp > 10:
            coef =0.1
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

        locallow = nanargmax_new(data['high'][-int(nanmax_np([1, aaa * coef])):])
        
        fac1 = (data['last_to_mid'][-451:])
        fac = nanmean_np(fac1[locallow:])

        if ('SC' in self.ticker) or ('AU' in self.ticker) or ('CU' in self.ticker) or ('SN' in self.ticker):
            fac = -fac
        return -fac
    def pre_calculate(self, data):
        pass
    
        
    
        
        