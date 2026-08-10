from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_90_df(FutureFactor):


    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(2 * self.freq)
        self.required_columns = ['volume', 'close']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 1200
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.fac_list = []
        self.vmask_list = []


        
    def calculate(self, data):
        aaa = 45
        
        vmask = (data['volume'][-1] > np.nanquantile(data['volume'][-aaa:], 0.9))
        if len(np.array(data['close'][-aaa:])) < len(self.vmask_list[-aaa:]):
            return np.nan
        self.vmask_list.append(vmask)
        
        fac = (data['close'][-1] - nanmean_np(np.array(data['close'][-aaa:])[self.vmask_list[-aaa:]]))
        self.fac_list.append(fac)
        self.fac_list = list(nanforward_fill(np.array(self.fac_list)))
        return irr_filter_numba((self.fac_list[-50 :]), 10)[-1]
        
    def pre_calculate(self, data):
        self.fac_list = []
        self.vmask_list = []
        aaa = 45
        for i in range(150, -1, -1):
            if i == 0:
                dclose = data['close'][-aaa - 5 :]
                dvolume = data['volume'][-aaa - 5 :]
            else:
                dclose = data['close'][-aaa - 5 - i : -i]
                dvolume = data['volume'][-aaa - 5 - i: -i]
            if len(dvolume) > 1:
                vmask = (dvolume[-1] > np.nanquantile(dvolume[-aaa:], 0.9))
                self.vmask_list.append(vmask)
                if len(self.vmask_list) < aaa:
                    pass
                else:
                    lth = len(dclose[-aaa:])
                    fac = (dclose[-1] - nanmean_np(np.array(dclose[-aaa:])[self.vmask_list[-lth:]]))
                    self.fac_list.append(fac)
            else:
                self.vmask_list.append(False)
                self.fac_list.append(np.nan)

        
        
        