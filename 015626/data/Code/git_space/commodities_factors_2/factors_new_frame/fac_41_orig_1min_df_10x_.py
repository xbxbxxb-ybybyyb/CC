from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_41_orig_1min_df_10x_(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(7 * int(self.freq))
        self.required_columns = ['high']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 60000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.temp2_list = []

    
    def calculate(self, data):
        aaa = 20
        bbb = 1500
        ccc = 100
        ddd = 200

        dhigh = data['high'][-bbb - 1:]
        temp2 = nanmax_np(dhigh[-aaa:]) - nanmax_np(dhigh[-bbb:])
        self.temp2_list.append(temp2)
        factor = nanmean_np(self.temp2_list[-ccc:])
        return factor
        
        
    def pre_calculate(self, data):
        self.temp2_list = []
        aaa = 20
        bbb = 1500
        ccc = 100
        ddd = 200
        
        for i in range(ccc, -1, -1):
            if i == 0:
                dhigh = data['high'][-bbb:]

            else:
                dhigh = data['high'][-bbb - i : -i]

            temp2 = nanmax_np(dhigh[-aaa:]) - nanmax_np(dhigh[-bbb:])
            self.temp2_list.append(temp2)

            
        




                
                


        