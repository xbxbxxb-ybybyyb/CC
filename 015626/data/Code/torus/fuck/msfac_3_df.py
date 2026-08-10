from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class msfac_3_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * freq)
        self.required_columns = [ 'last_n_4_volume_secmain', 'last_n_4_ret_secmain', 'volume_secmain']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = 4500
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__
        self.factor_list = []
    
    def calculate(self, data):

        ba = data['last_n_4_volume_secmain'][-160:]
        ret10 = data['last_n_4_ret_secmain'][-160:]
        volume = data['volume_secmain'][-160:]
        fac_raw = (ret10 * (ba / r(volume)))

        fac = ts_reg_beta(fac_raw, 150)[-1]

        return fac
        
    def pre_calculate(self, data):
        pass




                
                


        