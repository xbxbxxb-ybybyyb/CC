from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_92_adj_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(1801 / self.bars_dict[self.ticker])) * self.freq)
        self.required_columns = [ 'low', 'BidAskSpreadMean', 'close']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 3000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__


    def calculate(self, data):
        hclose = data['close'][-31:]
        coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(data['BidAskSpreadMean'][-30:]))
        
        aaa = 600
        
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
            coef = 4

        locallow = nanargmax_new(data['low'][-int(nanmax_np([1, aaa * coef])):])
        
        dclose = (data['close'][-1801:])
        fac1 = dclose[1:] - dclose[:-1]
        fac = nanmean_np(fac1[locallow:]) / r(nanstd_np(fac1[locallow:]))

        return fac
    def pre_calculate(self, data):
        pass
        