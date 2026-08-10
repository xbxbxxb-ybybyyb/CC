from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_ms_2_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * freq)
        self.required_columns = [ 'buy_active', 'sell_active']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 600
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.fac_raw_list = []
        self.fac_list = []
    

    
    def calculate(self, data):
        if ('czc' in self.ticker.lower()) or ('zce' in self.ticker.lower()):
            return 0


        ba = data['buy_active'][-150:]
        sa = data['sell_active'][-150:]


        fac = (ba / r(sa))
        factor = irr_filter_raw(fac, 30)[-1]
        return factor
        
    def pre_calculate(self, data):
        pass




                
                


        