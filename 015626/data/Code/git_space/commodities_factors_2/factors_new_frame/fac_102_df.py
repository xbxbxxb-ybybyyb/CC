from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_102_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(600 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [ 'last_to_weighted_mid', 'tday']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 1000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.fac_list = []

    def calculate(self, data):

        ddt = np.array(data['tday'][-555:])
        mk = len(ddt[ddt == ddt[-1]])
        fac = nanmean_np(data['last_to_weighted_mid'][-mk:])
        self.fac_list.append(fac)
        fac1 = irr_filter_raw(self.fac_list[-15:], 3)[-1]
        if ('SC' in self.ticker) or ('CU' in self.ticker) or ('SN' in self.ticker):
            fac1 = -fac1
        return -fac1
    def pre_calculate(self, data):
        self.fac_list = []
        for i in range(20, -1, -1):
            if i == 0:
                ddt = np.array(data['tday'][-555 - i:])
                bsv = data['last_to_weighted_mid'][-555 - i:]

            else:
                ddt = np.array(data['tday'][-555 - i: -i])
                bsv = data['last_to_weighted_mid'][-555 - i: -i]
            if len(ddt) < 1:
                self.fac_list.append(np.nan)
                continue
                
            mk = len(ddt[ddt == ddt[-1]])
    
            fac = nanmean_np(bsv[-mk:])
            self.fac_list.append(fac)
            


        