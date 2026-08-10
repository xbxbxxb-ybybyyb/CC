from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_96_adj_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(1231 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [ 'buy_small_volume', 'BidAskSpreadMean', 'close_secmain', 'sell_small_volume', 'close']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = 2400
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__


    def calculate(self, data):
        hclose = data['close'][-31:]
        coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(data['BidAskSpreadMean'][-30:]))
        dclose_main = data['close'][-1213:]
        dclose_secmain = data['close_secmain'][-1213:]
        aaa = 400
        
        if coef_temp > 10:
            coef =0.2
        elif (coef_temp > 6) and (coef_temp <= 10):
            coef = 0.5
        elif (coef_temp > 4) and (coef_temp <= 6):
            coef = 1
        elif (coef_temp > 3) and (coef_temp <= 4):
            coef =2
        elif (coef_temp <= 3):
            coef = 3
        else:
            coef = 6

        close_diff_main = dclose_main[12:] - dclose_main[:-12]
        close_diff_secmain = dclose_secmain[12:] - dclose_secmain[:-12]
        close_diff = close_diff_main - close_diff_secmain
        locallow = nanargmax_new(close_diff[-int(nanmax_np([1, aaa * coef])):])
        

        fac1 = data['buy_small_volume'][-1200:] - data['sell_small_volume'][-1200:]
        fac = -nanmean_np(fac1[locallow:])
        if ('SC' in self.ticker) or ('AU' in self.ticker) or ('CU' in self.ticker) or ('SN' in self.ticker):
            fac = -fac
        return fac#nanstd_np(fac1[locallow:])
    def pre_calculate(self, data):
        pass




                
                


        