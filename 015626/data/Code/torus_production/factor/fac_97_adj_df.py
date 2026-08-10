from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_97_adj_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(801 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [  'close', 'BidAskSpreadMean',  'buy_active', 'sell_active']
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
        dclose = data['close'][-801:]

        aaa = 400
        
        if coef_temp > 10:
            coef =0.5
        elif (coef_temp > 6) and (coef_temp <= 10):
            coef = 0.75
        elif (coef_temp > 4) and (coef_temp <= 6):
            coef = 1
        elif (coef_temp > 3) and (coef_temp <= 4):
            coef = 1.5
        elif (coef_temp <= 3):
            coef = 2
        else:
            coef = 6

        close_diff = dclose[30:] - dclose[:-30]
        localhigh = nanargmax_new(close_diff[-int(nanmax_np([1, aaa * coef])):]) 

        fac = data['buy_active'][-801:] - data['sell_active'][-801:]
        
        fac1 = nanmean_np(fac[localhigh:])
        return fac1
    def pre_calculate(self, data):
        pass

        