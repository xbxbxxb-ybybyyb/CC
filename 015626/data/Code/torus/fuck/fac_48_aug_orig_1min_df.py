from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np
import numpy as np
from numba import njit
from utils_zsj import SMA



class fac_48_aug_orig_1min_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * int(freq))
        self.required_columns = [ 'close_secmain', 'high_secmain']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = 3000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__

        self.vol_list = []
        self.sig_list = []


    
    def calculate(self, data):

        
        aaa = 3
        bbb = 22
        ccc = 22
        ddd = 10
                
        hclose = data['close_secmain'][-aaa - bbb:]
        hhigh = data['high_secmain'][-bbb - aaa:]
        
        rtn = data['close_secmain'][aaa:] - data['close_secmain'][:-aaa]
        
        vol = nanstd_np(rtn[-bbb:], ddof = 1)
        
        
        if vol < 1e-8:
            vol = np.nan
        self.vol_list.append(vol)
        ret = hclose[-1] - nanmax_np(hhigh[:-aaa][-bbb:]) - 1
        sig = (ret / (vol))
        self.sig_list.append(sig)
        sig_final = nanmean_np(self.sig_list[-3:])
        return sig_final


    
    def pre_calculate(self, data):
        aaa = 3
        bbb = 22
        ccc = 22
        ddd = 10
        
        for i in range(50, -1, -1):
            if i == 0:
                hclose = data['close_secmain'][-aaa - bbb:]
                hhigh = data['high_secmain'][-bbb - aaa:]  

            else:
                hclose = data['close_secmain'][-aaa - bbb - i: -i]
                hhigh = data['high_secmain'][-bbb - aaa - i: -i]  
            if len(hclose) > 1:
                rtn = hclose[aaa:] - hclose[:-aaa]
                vol = nanstd_np(rtn[-bbb:], ddof = 1)
                
                if vol < 1e-8:
                    vol = np.nan
                self.vol_list.append(vol)
                ret = hclose[-1] - nanmax_np(hhigh[:-aaa][-bbb:]) - 1

                sig = (ret / (vol))
                self.sig_list.append(sig)
            else:
                self.vol_list.append(np.nan)
                self.sig_list.append(np.nan)