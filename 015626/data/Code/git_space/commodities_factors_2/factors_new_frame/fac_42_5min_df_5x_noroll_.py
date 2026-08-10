from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_42_5min_df_5x_noroll_(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(26 * int(self.freq))
        self.required_columns = ['high', 'low', 'close']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 15000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.sig_list = []

    
    def calculate(self, data):
        aaa = 5	
        bbb = 8	
        ccc = 50

        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        w1 = int(coef * aaa / 5)
        w2 = int(coef)
        w3 = int(coef * aaa * 5)
        dhigh = data['high'][-w3:]
        dlow = data['low'][-w3:]
        dclose = data['close'][-w3:]

        
        hh = nanmax_np(dhigh[-w1:])
        ll = nanmin_np(dlow[-w1:])
        sig1 = (2 * dclose[-1] / (hh + ll))

        hh = nanmax_np(dhigh[-w2:])
        ll = nanmin_np(dlow[-w2:])
        sig2 = (2 * dclose[-1] / (hh + ll))

        hh = nanmax_np(dhigh[-w3:])
        ll = nanmin_np(dlow[-w3:])
        sig3 = (2 * dclose[-1] / (hh + ll))

        sig = (sig1 +  sig2 + sig3 * 2)
        self.sig_list.append(sig)

        sig11 = ema_1(self.sig_list[-40:], 40, 1/9) + sig
        return sig11
        
        
        
    def pre_calculate(self, data):
        self.sig_list = []

        aaa = 5	
        bbb = 8	
        ccc = 50
        
        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        w1 = int(coef * aaa / 5)
        w2 = int(coef)
        w3 = int(coef * aaa * 5)
        
        for i in range(42, -1, -1):
            if i == 0:
                dhigh = data['high'][-w3:]
                dlow = data['low'][-w3:]
                dclose = data['close'][-w3:]

            else:
                dhigh = data['high'][-w3 - i: -i]
                dlow = data['low'][-w3 - i: -i]
                dclose = data['close'][-w3 - i: -i]

            if (len(dhigh) == 0) or (len(dlow) == 0) or (len(dclose) == 0):
                self.sig_list.append(np.nan)
            else:
                hh = nanmax_np(dhigh[-w1:])
                ll = nanmin_np(dlow[-w1:])
                sig1 = (2 * dclose[-1] / (hh + ll))
        
                hh = nanmax_np(dhigh[-w2:])
                ll = nanmin_np(dlow[-w2:])
                sig2 = (2 * dclose[-1] / (hh + ll))
        
                hh = nanmax_np(dhigh[-w3:])
                ll = nanmin_np(dlow[-w3:])
                sig3 = (2 * dclose[-1] / (hh + ll))
        
                sig = (sig1 +  sig2 + sig3 * 2)
                self.sig_list.append(sig)

            
        




                
                


        