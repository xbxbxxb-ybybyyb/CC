from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class msfac_2_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * self.freq)
        self.required_columns = [ 'first_10_volume_secmain', 'first_10_ret_secmain', 'volume_secmain']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = int(int(self.bars_dict[self.ticker]) / int(self.freq))
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__
        self.factor_list = []
    
    def calculate(self, data):

        ba = data['first_10_volume_secmain'][-1]
        ret10 = data['first_10_ret_secmain'][-1]
        volume = data['volume_secmain'][-1]
        fac_raw = (ret10 * (ba / r(volume)))
        if np.isnan(fac_raw):
            if len(self.factor_list) > 0:
                fac_raw = 0
        self.factor_list.append(fac_raw)
        fac = ema_1(self.factor_list[-100:], 100, 1/(20 + 1))

        return fac
        
    def pre_calculate(self, data):
        self.factor_list = []
        for i in range(105, -1, -1):
            try:
                ba = data['first_10_volume_secmain'][-1-i]
                ret10 = data['first_10_ret_secmain'][-1-i]
                volume = data['volume_secmain'][-1-i]

                fac_raw = (ret10 * (ba / r(volume)))
                if np.isnan(fac_raw):
                    if len(self.factor_list) > 0:
                        fac_raw = 0
                    else:
                        pass
                self.factor_list.append(fac_raw)
            except:
                self.factor_list.append(np.nan)
            




                
                


        