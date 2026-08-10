from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class msfac_12_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * self.freq)
        self.required_columns = [ 'PxVolCorr']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 3000
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__
        self.factor_list = []
    
    def calculate(self, data):

        mid = nanmean_np(data['PxVolCorr'][-10:]) / r(nanstd_np(data['PxVolCorr'][-10:], ddof = 1))
        self.factor_list.append(mid)
        fac = ema_1(self.factor_list[-10:], 10, 1/5)
        
        return fac
        
    def pre_calculate(self, data):
        self.factor_list = []
        for i in range(30, -1, -1):
            if i== 0:
                lr = data['PxVolCorr'][-10:]
            else:
                lr = data['PxVolCorr'][-10-i:-i]

            mid = nanmean_np(lr) / r(nanstd_np(lr, ddof = 1))
            self.factor_list.append(mid)
            
            




                
                


        