from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_92_adj_s_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(2251 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [ 'low_secmain', 'BidAskSpreadMean_secmain', 'close_secmain']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = 3000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__


    def calculate(self, data):
        hclose = data['close_secmain'][-31:]
        coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(data['BidAskSpreadMean_secmain'][-30:]))
        
        aaa = 750
        
        if coef_temp > 10:
            coef =0.2
        elif (coef_temp > 6) and (coef_temp <= 10):
            coef = 0.5
        elif (coef_temp > 4) and (coef_temp <= 6):
            coef = 1
        elif (coef_temp > 3) and (coef_temp <= 4):
            coef =1.5
        elif (coef_temp <= 3):
            coef = 2
        else:
            coef = 6

        locallow = nanargmax_new(data['low_secmain'][-int(nanmax_np([1, aaa * coef])):])
        
        dclose = (data['close_secmain'][-2251:])
        fac1 = dclose[1:] - dclose[:-1]
        fac = nanmean_np(fac1[locallow:])

        return fac
    def pre_calculate(self, data):
        pass
        
        