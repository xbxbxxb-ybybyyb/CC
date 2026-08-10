from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np

def irr_filter2(data, coef, bbb):
    window = bbb
    sig1_list = nanforward_fill(data[-window * 6 :])
    return irr_filter(sig1_list[-int(window * coef):], int(window * coef))[-1]


class fac_81_adj_df(FutureFactor):


    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(3 * self.freq)
        self.required_columns = ['buy_small_volume', 'sell_small_volume', 'close', 'BidAskSpreadMean']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 1200
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.temp2_list = []
        self.temp4_list = []


        
    def calculate(self, data):
        hclose = data['close'][-31:]
        coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(data['BidAskSpreadMean'][-30:]))
        
        aaa = 90
        
        if coef_temp > 10:
            coef =0.1
        elif (coef_temp > 6) and (coef_temp <= 10):
            coef = 0.5
        elif (coef_temp > 4) and (coef_temp <= 6):
            coef = 1
        elif (coef_temp > 3) and (coef_temp <= 4):
            coef = 1.5
        elif (coef_temp <= 3):
            coef = 2
        else:
            coef = 6
            
        fac = (data['buy_small_volume'][-540:]- data['sell_small_volume'][-540:])
        
        fac1 = irr_filter4(-fac, coef, aaa)
        if ('SC' in self.ticker) or ('AU' in self.ticker) or ('CU' in self.ticker) or ('SN' in self.ticker):
            fac1 = -fac1

        return fac1
        
    def pre_calculate(self, data):
        pass


        
        