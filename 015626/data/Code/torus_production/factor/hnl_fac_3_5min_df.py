from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_3_5min_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(1000 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [ 'close', 'high', 'tday']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 1500
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.fac_raw_list = []
        self.fac_list = []
    
    def calculate(self, data):

        dclose = data['close'][-555:]
        dhigh = data['high'][-555:]
        ddt = np.array(data['tday'][-555:])
        mk = len(ddt[ddt == ddt[-1]])
        
        fac = dclose[-1] / nanmax_np(dhigh[-mk:]) - 1
        self.fac_list.append(fac)
        
        fac1 = rolling_norm_raw(self.fac_list[-20:], 20)
        fac2 = rolling_norm_raw(self.fac_list[-180:], 180)
        fac_raw = fac1 + fac2
        self.fac_raw_list.append(fac_raw)
        return irr_filter_raw(self.fac_raw_list[-15:], 3)[-1]
        
    def pre_calculate(self, data):
        for i in range(240, -1, -1):
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
                try:
                    fac = dclose[-1] / nanmax_np(dhigh[-mk:]) - 1
                    self.fac_list.append(fac)
                except:
                    self.fac_list.append(np.nan)
                if len(self.fac_list) >= 180:
                    fac1 = rolling_norm_raw(self.fac_list[-20:], 20)
                    fac2 = rolling_norm_raw(self.fac_list[-180:], 180)
                    fac_raw = fac1 + fac2
                    self.fac_raw_list.append(fac_raw)
            except:
                self.fac_list.append(np.nan)
                self.fac_raw_list.append(np.nan)




                
                


        