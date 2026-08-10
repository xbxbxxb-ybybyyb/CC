from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_73_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(350 / self.bars_dict[self.ticker])) * self.freq)
        self.required_columns = ['idmax', 'idmin', 'high', 'low', 'close']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 2500
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.factor_list = []

    def calculate(self, data):

        dclose = data['close'][-241:]
        dhigh = data['high'][-341:]
        dlow = data['low'][-341:]
        didmax = data['idmax'][-341:]
        didmin = data['idmin'][-341:]
        
        
        factor = ema_1(((dhigh[-100:] - dlow[-100:]) / r(didmax[-100:] - didmin[-100:])), 100, 1/31)
        self.factor_list.append(factor)
        localhigh = nanargmax_new(self.factor_list[-240:])
        fac1 = (dclose[1:] -dclose[:-1])
        fac = nanmean_np(fac1[localhigh:]) + irr_filter_raw(fac1[localhigh:], len(fac1[localhigh:]))[-1]

        return fac
        
    def pre_calculate(self, data):
        for i in range(245, -1, -1):
            if i == 0:
                dclose = data['close'][-241:]
                dhigh = data['high'][-341:]
                dlow = data['low'][-341:]
                didmax = data['idmax'][-341:]
                didmin = data['idmin'][-341:]
            else:
                dclose = data['close'][-241 - i: -i]
                dhigh = data['high'][-341 - i: -i]
                dlow = data['low'][-341 - i: -i]
                didmax = data['idmax'][-341 - i: -i]
                didmin = data['idmin'][-341 - i: -i]
                
            
            
            factor = ema_1(((dhigh[-100:] - dlow[-100:]) / r(didmax[-100:] - didmin[-100:])), 100, 1/31)
            self.factor_list.append(factor)
        
        