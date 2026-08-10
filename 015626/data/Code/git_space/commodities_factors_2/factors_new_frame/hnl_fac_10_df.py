from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_10_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(800 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [ 'close', 'tday']
        self.instrument_type = 'main' #second_main
        self.normalize_size = int(3000 / int(self.freq))
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__
        self.fac_list = []

    def calculate(self, data):

        unit = int(self.freq)
        ddt = np.array(data['tday'][-555:])
        mk = len(ddt[ddt == ddt[-1]])
        fac = data['close'][-1] / nanmean_np(data['close'][-mk:]) - 1
        self.fac_list.append(fac)
        
        fac1 = rolling_norm_raw(self.fac_list, int(120 / unit)) - rolling_norm_raw(self.fac_list, nanmin_np([int(10 / unit), 5]))
        return fac1
    def pre_calculate(self, data):
        self.fac_list = []
        for i in range(121, -1, -1):
            if i == 0:
                ddt = np.array(data['tday'][-555 - i:])
                dclose = data['close'][-555 - i:]

            else:
                ddt = np.array(data['tday'][-555 - i: -i])
                dclose = data['close'][-555 - i: -i]
            if len(dclose) > 1:

                unit = int(self.freq)
                mk = len(ddt[ddt == ddt[-1]])
                fac = dclose[-1] / nanmean_np(dclose[-mk:]) - 1
                self.fac_list.append(fac)
            else:
                self.fac_list.append(np.nan)
                


        