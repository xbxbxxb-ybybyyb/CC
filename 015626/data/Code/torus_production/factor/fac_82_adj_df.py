from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_82_adj_df(FutureFactor):


    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(901 / self.bars_dict[self.ticker])) * self.freq)
        self.required_columns = ['volume', 'close', 'BidAskSpreadMean']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 1200
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.input_signal_list = []
        self.y_list = []
        self.fuck_list = []


        
    def calculate(self, data):
        hclose = data['close'][-31:]
        coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(data['BidAskSpreadMean'][-30:]))
        dclose = data['close'][-901:]
        dvolume = data['volume'][-900:]
        aaa = 180
        
        if coef_temp > 10:
            coef =0.1
        elif (coef_temp > 6) and (coef_temp <= 10):
            coef = 0.5
        elif (coef_temp > 4) and (coef_temp <= 6):
            coef = 1
        elif (coef_temp > 3) and (coef_temp <= 4):
            coef = 2
        elif (coef_temp <= 3):
            coef = 5
        else:
            coef = 6
        
        if len(dclose) - 1 == len(dvolume):

            fac = (dclose[1:] - dclose[:-1]) * dvolume

        elif len(dclose) == len(dvolume):
            fac = (dclose[1:] - dclose[:-1]) * dvolume[1:]
        else:
            fac = np.nan
        
        fac1 = irr_filter4(fac, coef, aaa)


        return fac1
        
    def pre_calculate(self, data):
        pass
        
        