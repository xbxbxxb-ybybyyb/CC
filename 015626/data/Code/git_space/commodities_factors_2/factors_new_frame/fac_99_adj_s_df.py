from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_99_adj_s_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(1231 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [ 'sell_gigantic_volume', 'BidAskSpreadMean_secmain', 'close_secmain', 'buy_gigantic_volume', 'buy_small_volume', 'sell_small_volume']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = 2400
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__


    def calculate(self, data):
        hclose = data['close_secmain'][-31:]
        coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(data['BidAskSpreadMean_secmain'][-30:]))
        dclose_main = data['close_secmain'][-1213:]

        
        coef = coef_temp
        if np.isnan(coef_temp):
            coef = 6
        if (coef_temp > 6):
            coef = 0.5
        if (coef_temp > 3) and (coef_temp <= 6):
            coef = 1
        if (coef_temp > 3) and (coef_temp <= 4):
            coef =1.5


        bps = data['buy_gigantic_volume'][-600:] + data['sell_gigantic_volume'][-600:]
        bms = data['buy_gigantic_volume'][-600:] - data['sell_gigantic_volume'][-600:]


        
        localhigh1 = nanargmax_new(bps[-int(nanmax_np([1, 200 * coef])):])
        localhigh2 = nanargmax_new(bms[-int(nanmax_np([1, 150 * coef])):])
        fac1 = data['buy_small_volume'][-600:] - data['sell_small_volume'][-600:]
        fac = -nanmean_np(fac1[localhigh1:]) -nanmean_np(fac1[localhigh2:])
        if ('SC' in self.ticker) or ('AU' in self.ticker) or ('CU' in self.ticker) or ('SN' in self.ticker):
            fac = -fac
        return fac#nanstd_np(fac1[locallow:])
    def pre_calculate(self, data):
        pass




                
                


        