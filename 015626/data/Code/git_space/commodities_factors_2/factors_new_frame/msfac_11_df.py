from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class msfac_11_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * self.freq)
        self.required_columns = [ 'last_n_4_ret', 'last_n_4_ret_secmain']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 3000
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__
        self.factor_list = []
    

    
    def calculate(self, data):



        mid1 = nanmean_np(data['last_n_4_ret'][-15:]) / r(nanstd_np(data['last_n_4_ret'][-15:]))
        mid2 = nanmean_np(data['last_n_4_ret_secmain'][-15:]) / r(nanstd_np(data['last_n_4_ret_secmain'][-15:]))
        mid = nanmean_np([mid1, mid2])
        self.factor_list.append(mid)
        fac = ema_1(np.array(self.factor_list[-10:]), 10, 1/4)
        
        return fac
        
    def pre_calculate(self, data):
        self.factor_list = []
        for i in range(15, -1, -1):
            if i == 0:
                mid1 = nanmean_np(data['last_n_4_ret'][-15:]) / r(nanstd_np(data['last_n_4_ret'][-15:]))
                mid2 = nanmean_np(data['last_n_4_ret_secmain'][-15:]) / r(nanstd_np(data['last_n_4_ret_secmain'][-15:]))
            else:
                mid1 = nanmean_np(data['last_n_4_ret'][-15 - i: -i]) / r(nanstd_np(data['last_n_4_ret'][-15 - i: -i:]))
                mid2 = nanmean_np(data['last_n_4_ret_secmain'][-15 - i: -i:]) / r(nanstd_np(data['last_n_4_ret_secmain'][-15 - i: -i:]))
            mid = nanmean_np([mid1, mid2])
            self.factor_list.append(mid)
            
        




                
                


        