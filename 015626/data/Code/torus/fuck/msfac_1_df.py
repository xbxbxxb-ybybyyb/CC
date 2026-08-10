from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class msfac_1_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * self.freq)
        self.required_columns = [ 'last_n_4_volume_secmain', 'last_n_4_ret_secmain', 'volume_secmain']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = 3000
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__
        self.factor_list = []
    
    def calculate(self, data):

        ba = data['last_n_4_volume_secmain'][-1]
        ret10 = data['last_n_4_ret_secmain'][-1]
        volume = data['volume_secmain'][-1]
        fac_raw = (ret10 * (ba / r(volume)))
        if np.isnan(fac_raw):
            if len(self.factor_list) > 0:
                fac_raw = 0
        self.factor_list.append(fac_raw)
        fac = ema_1(self.factor_list[-180:], 180, 1/(30 + 1))

        return fac
        
    def pre_calculate(self, data):
        for i in range(185, -1, -1):
            if len(data['last_n_4_volume_secmain']) > 1 + i:
                ba = data['last_n_4_volume_secmain'][-1-i]
                ret10 = data['last_n_4_ret_secmain'][-1-i]
                volume = data['volume_secmain'][-1-i]

                fac_raw = (ret10 * (ba / r(volume)))
                if np.isnan(fac_raw):
                    if len(self.factor_list) > 0:
                        fac_raw = 0
                    else:
                        pass
                self.factor_list.append(fac_raw)
            else:
                self.factor_list.append(np.nan)
            




                
                


        