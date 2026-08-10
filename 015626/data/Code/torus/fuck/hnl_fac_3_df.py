from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_3_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(600 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [ 'close', 'high', 'tday']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 3000
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__

        self.fac_list = []
    
    def calculate(self, data):

        dclose = data['close'][-555:]
        dhigh = data['high'][-555:]
        ddt = np.array(data['tday'][-555:])
        mk = len(ddt[ddt == ddt[-1]])
        
        fac = dclose[-1] / nanmax_np(dhigh[-mk:]) - 1
        self.fac_list.append(fac)
        
        fac1 = rolling_norm_raw(self.fac_list[-180:], 180)
        return fac1
        
    def pre_calculate(self, data):
        for i in range(201, -1, -1):
            if i == 0:
                dclose = data['close'][-555 - i:]
                dhigh = data['high'][-555 - i:]
                ddt = np.array(data['tday'][-555 - i:])

            else:
                dclose = data['close'][-555 - i: -i]
                dhigh = data['high'][-555 - i: -i]
                ddt = np.array(data['tday'][-555 - i: -i])
 
            unit = int(self.freq)        
            coef = int(int(self.bars_dict[self.ticker]) / int(self.freq))
            
            try:
                mk = len(ddt[ddt == ddt[-1]])
                fac = dclose[-1] / nanmax_np(dhigh[-mk:]) - 1
                self.fac_list.append(fac)
            except:
                self.fac_list.append(np.nan)



                
                


        