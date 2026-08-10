from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_39_adj_df(FutureFactor):
    required_columns = ['close', 'BidAskSpreadMean', 'high']

    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(6 * freq)
        self.required_columns = ['close', 'BidAskSpreadMean', 'high']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 3000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.sig1_list = []
        self.rtn_list = []
        
    def calculate(self, data):
        hclose = data['close'][-31:]
        coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(data['BidAskSpreadMean'][-30:]))

        
        if coef_temp > 10:
            coef =0.1
        elif (coef_temp > 6) and (coef_temp <= 10):
            coef = 0.3
        elif (coef_temp > 4) and (coef_temp <= 6):
            coef = 1
        elif (coef_temp > 3) and (coef_temp <= 4):
            coef = 2
        elif (coef_temp <= 3):
            coef = 5
        else:
            coef = 6

        aaa = 210
        ccc = 10
        

        dclose = data['close'][-aaa * 5 - 5 :]

        rtn = dclose[1:] - dclose[:-1]
        vol = nanstd_np(rtn[-int(coef * aaa):])
        
        ret = dclose[-1] - nanmax_np(data['high'][-int(coef * aaa) - 1 :-1])
        sig = ret * r(vol)
        return sig

    def pre_calculate(self, data):
        pass
        