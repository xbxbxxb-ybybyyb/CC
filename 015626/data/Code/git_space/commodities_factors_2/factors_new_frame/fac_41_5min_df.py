from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_41_5min_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(21 * int(self.freq))
        self.required_columns = ['high',  'close', 'dt']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 0
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.input_signal_list = []
        self.temp2_list = []
        self.fac_list = []
        self.factor_norm_list = []
    
    def calculate(self, data):
        aaa = 2
        bbb = 150
        ccc = 10
        ddd = 10
        
        
        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        dclose = data['close'][-coef * 5:]
        temp2 = nanmax_np(data['high'][-aaa:]) - nanmax_np(data['high'][-bbb:])
        self.temp2_list.append(temp2)
        factor = irr_filter_raw(self.temp2_list[-ccc*6:], ccc)[-1]
        self.fac_list.append(factor)
        fac_norm = rank_data(self.fac_list[-ddd * 300:])
        self.factor_norm_list.append(fac_norm)
        fac_short = self.factor_norm_list[-coef:]
        hclose_short = dclose[-coef:]

        cs = new_corr(fac_short, hclose_short)
        
        fac_long = self.factor_norm_list[-coef * 5:]
        hclose_long = dclose[-coef * 5:]

        cl = new_corr(fac_long, hclose_long)

        if (cs < cl) or (cl < 0):
            return 0
        else:
            return fac_norm

        
        
    def pre_calculate(self, data):
        self.input_signal_list = []
        self.temp2_list = []
        self.fac_list = []
        self.factor_norm_list = []
        aaa = 2
        bbb = 150
        ccc = 10
        ddd = 10
        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        for i in range(int(3300 + coef * 5), -1, -1):
            if i == 0:
                dhigh = data['high'][-bbb:]

            else:
                dhigh = data['high'][-bbb - i : -i]

            
            temp2 = nanmax_np(dhigh[-aaa:]) - nanmax_np(dhigh[-bbb:])
            self.temp2_list.append(temp2)
            factor = irr_filter_raw(self.temp2_list[-ccc*6:], ccc)[-1]
            self.fac_list.append(factor)
            fac_norm = rank_data(self.fac_list[-ddd * 300:])
            self.factor_norm_list.append(fac_norm)
            
        




                
                


        