from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_42_df_5x_noroll_(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(30 * int(self.freq))
        self.required_columns = ['high', 'low', 'close']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 0
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.sig_list = []
        self.factor_norm_list = []
        self.sig_mean_list = []
    
    def calculate(self, data):


        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        aaa = 5
        bbb = 2
        ccc = 10
        
        w1 = int(coef * aaa / 10)
        w2 = int(coef)
        w3 = int(coef * aaa * 5)
        dhigh = data['high'][-w3:]
        dlow = data['low'][-w3:]
        dclose = data['close'][-w3:]
  
        hh = nanmax_np(dhigh[-w1:])
        ll = nanmin_np(dlow[-w1:])
        sig1 = (2 * dclose[-1] / (hh + ll))


        hh = nanmax_np(dhigh[-w3:])
        ll = nanmin_np(dlow[-w3:])
        sig3 = (2 * dclose[-1] / (hh + ll))

        sig = (sig1 * 2 +  sig3)
        self.sig_list.append(sig)

        sig = nanmean_np(self.sig_list[-bbb:])
        self.sig_mean_list.append(sig)
        fac_norm = rank_data(self.sig_mean_list[-ccc * coef:])
        self.factor_norm_list.append(fac_norm)

        
        fac_short = self.factor_norm_list[-coef:]
        hclose_short = dclose[-coef:]

        cs = new_corr(fac_short, hclose_short)
        
        fac_long = self.factor_norm_list[-coef * 3:]
        hclose_long = dclose[-coef * 3:]

        cl = new_corr(fac_long, hclose_long)

        if (cs < cl) or (cl < 0):
            return 0
        else:
            return fac_norm

        
        
        
    def pre_calculate(self, data):


        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        aaa = 5
        bbb = 2
        ccc = 10
        
        w1 = int(coef * aaa / 10)
        w2 = int(coef)
        w3 = int(coef * aaa * 5)
        
        for i in range(coef * 15 + 10, -1, -1):
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
        
        
                hh = nanmax_np(dhigh[-w3:])
                ll = nanmin_np(dlow[-w3:])
                sig3 = (2 * dclose[-1] / (hh + ll))
        
                sig = (sig1 * 2 +  sig3)
                self.sig_list.append(sig)
        
                sig = nanmean_np(self.sig_list[-bbb:])
                self.sig_mean_list.append(sig)
                fac_norm = rank_data(self.sig_mean_list[-ccc * coef:])
                self.factor_norm_list.append(fac_norm)

            
        




                
                


        