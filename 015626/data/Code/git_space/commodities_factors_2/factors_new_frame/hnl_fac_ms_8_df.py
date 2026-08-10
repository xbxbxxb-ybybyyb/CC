from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_ms_8_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * freq)
        self.required_columns = [ 'low', 'buy_active', 'sell_active']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 600
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__
        self.fac_raw_list = []
        self.fac_list = []
    
    def calculate(self, data):
        if ('czc' in self.ticker.lower()) or ('zce' in self.ticker.lower()):
            return 0

        dlow = data['low'][-90:]
        ba = data['buy_active'][-90:]
        sa = data['sell_active'][-90:]

        
        locallow = nanargmin_new(dlow)

        fac = (ba / r(sa))
        factor = nanmean_np(fac[locallow:]) 
        return factor
        
    def pre_calculate(self, data):
        pass




                
                


        