from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_4_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(1500 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [ 'close', 'low', 'tday']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 1000
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__

        self.fac_list = []
    
    def calculate(self, data):

        dclose = data['close'][-555:]
        dlow = data['low'][-555:]
        ddt = np.array(data['tday'][-555:])
        try:
            mk = len(ddt[ddt == ddt[-1]])
            fac = dclose[-1] / nanmin_np(dlow[-mk:]) - 1
            self.fac_list.append(fac)
        except:
            self.fac_list.append(np.nan)
        
        fac1 = nanmean_np(self.fac_list[-7:]) / r(nanmean_np(self.fac_list[-360:]))
        return fac1
        
    def pre_calculate(self, data):
        for i in range(361, -1, -1):
            if i == 0:
                dclose = data['close'][-555 - i:]
                dlow = data['low'][-555 - i:]
                ddt = np.array(data['tday'][-555 - i:])

            else:
                dclose = data['close'][-555 - i: -i]
                dlow = data['low'][-555 - i: -i]
                ddt = np.array(data['tday'][-555 - i: -i])
 
            unit = int(self.freq)        
            coef = int(int(self.bars_dict[self.ticker]) / int(self.freq))
            
            try:
                mk = len(ddt[ddt == ddt[-1]])
                fac = dclose[-1] / nanmin_np(dlow[-mk:]) - 1
                self.fac_list.append(fac)
            except:
                self.fac_list.append(np.nan)


                
                


        