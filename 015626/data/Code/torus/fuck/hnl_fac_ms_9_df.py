from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_ms_9_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(2 * freq)
        self.required_columns = [ 'low', 'high', 'twap', 'volume']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 900
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__
        self.fac_raw_list = []
        self.fac_list = []
    
    def calculate(self, data):

        dlow = data['low'][-240:]
        dhigh = data['high'][-180:]
        twap = data['twap'][-241:]
        dvolume = data['volume'][-240:]
        
        locallow = nanargmin_new(dlow)
        localhigh = nanargmax_new(dhigh)

        if len(twap) -1 != len(dvolume):
            if len(twap) == len(dvolume):
                dvolume = dvolume[1:]
            else:
                return np.nan
        else:
            return np.nan

        fac = (twap[1:] - twap[:-1]) / r(dvolume)
        factor = nanmean_np(fac[locallow:]) + nanmean_np(fac[localhigh:])
        return factor
        
    def pre_calculate(self, data):
        pass




                
                


        