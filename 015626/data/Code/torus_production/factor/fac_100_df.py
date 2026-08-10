from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_100_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(600 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [ 'buy_small_volume', 'sell_small_volume', 'tday']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 2400
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.fac_list = []

    def calculate(self, data):
        ddt = np.array(data['tday'][-555:])
        mk = len(ddt[ddt == ddt[-1]])
        fac = nanmean_np(data['buy_small_volume'][-mk:] - data['sell_small_volume'][-mk:])
        self.fac_list.append(fac)
        fac1 = irr_filter_raw(self.fac_list[-15:], 3)[-1]
        
        if ('SC' in self.ticker) or ('CU' in self.ticker) or ('SN' in self.ticker):
            fac1 = -fac1
        return -fac1
    
    def pre_calculate(self, data):
        for i in range(20, -1, -1):
            if i == 0:
                ddt = np.array(data['tday'][-555 - i:])
                bsv = data['buy_small_volume'][-555 - i:]
                ssv = data['sell_small_volume'][-555 - i:]
            else:
                ddt = np.array(data['tday'][-555 - i: -i])
                bsv = data['buy_small_volume'][-555 - i: -i]
                ssv = data['sell_small_volume'][-555 - i: -i]
            if len(ddt) < 1:
                self.fac_list.append(np.nan)
            else:
                mk = len(ddt[ddt == ddt[-1]])
                fac = nanmean_np(bsv[-mk:] - ssv[-mk:])
                self.fac_list.append(fac)
            


        