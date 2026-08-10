from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np
import numpy as np
from numba import njit
from utils_zsj import SMA



class fac_49_df_5x_noroll_(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(8 * int(freq))
        self.required_columns = [ 'close_secmain', 'high_secmain', 'low_secmain']
        self.instrument_type = 'second_main' #second_main
        self.normalize_size = 1000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__

        self.temp2_list = []
        self.temp4_list = []


    
    def calculate(self, data):

        a = 900
        b = 300
        c = 5
        d = 5
                
        close = data['close_secmain'][-a:]
        high = data['high_secmain'][-a:]
        low = data['low_secmain'][-a:]
        low_n = nanmin_np(low[-a:])
        high_n = nanmax_np(high[-a:])
        temp1 = high_n - low_n
        if abs(temp1)<1e-8:
            temp1 = np.nan
        temp2 = (close[-1]- low_n) / r(high_n - low_n)
        self.temp2_list.append(temp2)
        b_low = nanmin_np(self.temp2_list[-b:])
        b_high = nanmax_np(self.temp2_list[-b:])
        temp3 = b_high - b_low
        if abs(temp3)<1e-8:
            temp3 = np.nan
        temp4 = (temp2 - b_low) / r(temp3)
        self.temp4_list.append(temp4)
        factor = temp4 +ema_span_1(self.temp4_list[-c*3:], c*3, c)
        return factor


    
    def pre_calculate(self, data):
        self.temp2_list = []
        self.temp4_list = []
        a = 900
        b = 300
        c = 5
        d = 5
                
        for i in range(310, -1, -1):
            if i == 0:
                close = data['close_secmain'][-a:]
                high = data['high_secmain'][-a:]
                low = data['low_secmain'][-a:] 

            else:
                close = data['close_secmain'][-a - i: -i]
                high = data['high_secmain'][-a - i: -i]
                low = data['low_secmain'][-a - i: -i]  

            if len(close) == 0:
                temp2 = np.nan
            else:
                low_n = nanmin_np(low[-a:])
                high_n = nanmax_np(high[-a:])
                temp1 = high_n - low_n
                if abs(temp1)<1e-8:
                    temp1 = np.nan
                temp2 = (close[-1]- low_n) / r(high_n - low_n)
            self.temp2_list.append(temp2)
            b_low = nanmin_np(self.temp2_list[-b:])
            b_high = nanmax_np(self.temp2_list[-b:])
            temp3 = b_high - b_low
            if abs(temp3)<1e-8:
                temp3 = np.nan
            temp4 = (temp2 - b_low) / r(temp3)
            self.temp4_list.append(temp4)