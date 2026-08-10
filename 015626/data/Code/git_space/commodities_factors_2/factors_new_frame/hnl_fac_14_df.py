from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_14_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(620 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [ 'twap', 'tday', 'volume']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 1000
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__

        self.fac_list = []
    
    def calculate(self, data):

        dclose = data['twap'][-556:]
        dvolume = data['volume'][-555:]
        ddt = np.array(data['tday'][-555:])
        mk = len(ddt[ddt == ddt[-1]])

        if len(dclose) == len(dvolume):
            ddiff = (dclose[1:] / dclose[:-1] - 1) / r(dvolume[1:].copy())
            fac = nansum_np(ddiff[-mk:])
        elif len(dclose)-1 == len(dvolume):
            ddiff = (dclose[1:] / dclose[:-1] - 1) / r(dvolume.copy())
            fac = nansum_np(ddiff[-mk:])
        else:
            fac = np.nan
        self.fac_list.append(fac)
        
        fac1 = rolling_norm_raw(self.fac_list[-25:], 25)
        return fac1
        
    def pre_calculate(self, data):
        self.fac_list = []
        for i in range(30, -1, -1):
            if i == 0:
                dclose = data['twap'][-556 - i:]
                ddt = np.array(data['tday'][-555 - i:])
                dvolume = data['volume'][-555 - i:]
            else:
                dclose = data['twap'][-556 - i: -i]
                ddt = np.array(data['tday'][-555 - i: -i])
                dvolume = data['volume'][-555 - i: -i]
            
            if len(ddt) > 1:
                mk = len(ddt[ddt == ddt[-1]])
                if len(dclose) == len(dvolume):
                    ddiff = (dclose[1:] / dclose[:-1] - 1) / r(dvolume[1:].copy())
                    fac = nansum_np(ddiff[-mk:])
                elif len(dclose)-1 == len(dvolume):
                    ddiff = (dclose[1:] / dclose[:-1] - 1) / r(dvolume.copy())
                    fac = nansum_np(ddiff[-mk:])
                else:
                    fac = np.nan
                self.fac_list.append(fac)
            else:
                self.fac_list.append(np.nan)
                


        