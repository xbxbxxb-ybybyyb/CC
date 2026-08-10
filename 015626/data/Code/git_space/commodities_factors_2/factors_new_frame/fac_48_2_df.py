from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np
import numpy as np
from numba import njit
from utils_zsj import SMA



class fac_48_2_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * int(freq))
        self.required_columns = [ 'close_secmain', 'high_secmain']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = int(2000 / int(freq))
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__


        self.vol_list = []
        self.sig_list = []


    
    def calculate(self, data):

        
        unit = int(self.freq)
        aaa = nanmax_np([int(2 / unit), 1])
        bbb = nanmax_np([int(15 / unit), 10])
        ccc = 3
        ddd = 3
        hclose = data['close_secmain'][-aaa - 10:]
        hhigh = data['high_secmain'][-bbb - aaa:]
        
        rtn = data['close_secmain'][aaa:] - data['close_secmain'][:-aaa]

        vol = nanstd_np(rtn[-10:], ddof = 1)
        
        
        if vol < 1e-8:
            vol = np.nan
        self.vol_list.append(vol)
        ret = hclose[-1] - nanmax_np(hhigh[:-aaa][-bbb:]) - 1
        co = cross_hub_num_array(self.vol_list, 10) + 1
        sig = (ret / (vol) / np.sqrt(co))
        self.sig_list.append(sig)
        sig_final = nanmean_np(self.sig_list[-ccc:])
        return sig_final


    
    def pre_calculate(self, data):
        self.vol_list = []
        self.sig_list = []

        unit = int(self.freq)
        aaa = nanmax_np([int(2 / unit), 1])
        bbb = nanmax_np([int(15 / unit), 10])
        ccc = 3
        ddd = 3
        
        for i in range(50, -1, -1):
            if i == 0:
                hclose = data['close_secmain'][-aaa - 10:]
                hhigh = data['high_secmain'][-bbb - aaa:]  

            else:
                hclose = data['close_secmain'][-aaa - 10 - i: -i]
                hhigh = data['high_secmain'][-bbb - aaa - i: -i]  

            if len(hclose) > 1:
                rtn = hclose[aaa:] - hclose[:-aaa]
                vol = nanstd_np(rtn[-bbb:], ddof = 1)
                
                if vol < 1e-8:
                    vol = np.nan
                self.vol_list.append(vol)
                ret = hclose[-1] - nanmax_np(hhigh[:-aaa][-bbb:]) - 1
            else:
                vol = np.nan
                self.vol_list.append(np.nan)
                ret = np.nan
            if len(self.vol_list) > 20:
                co = cross_hub_num_array(self.vol_list, 10) + 1
                sig = (ret / (vol) / np.sqrt(co))
                self.sig_list.append(sig)