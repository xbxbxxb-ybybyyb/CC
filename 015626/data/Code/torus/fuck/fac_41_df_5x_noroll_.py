from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_41_df_5x_noroll_(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(3 * int(self.freq))
        self.required_columns = ['high']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 15000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.temp2_list = []

    
    def calculate(self, data):
        aaa = 10
        bbb = 450
        ccc = 2
        ddd = 50

        dhigh = data['high'][-bbb - 1:]
        temp2 = nanmax_np(dhigh[-aaa:]) - nanmax_np(dhigh[-bbb:])
        self.temp2_list.append(temp2)
        vol = nanstd_np(dhigh[1:] - dhigh[:-1], ddof = 1)
        factor = (nanmean_np(self.temp2_list[-ccc:]) * r(np.sqrt(vol)))
        return factor
        
        
    def pre_calculate(self, data):
        aaa = 10
        bbb = 450
        ccc = 2
        ddd = 50
        
        for i in range(3, -1, -1):
            if i == 0:
                dhigh = data['high'][-bbb:]

            else:
                dhigh = data['high'][-bbb - i : -i]

            temp2 = nanmax_np(dhigh[-aaa:]) - nanmax_np(dhigh[-bbb:])
            self.temp2_list.append(temp2)

            
        




                
                


        