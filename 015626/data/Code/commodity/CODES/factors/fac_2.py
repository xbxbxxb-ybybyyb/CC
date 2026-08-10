import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
from operators_cc import *
import pandas as pd

class fac_2(FactorGenerator):
    def __init__(self):
        required_columns=['high', 'low', 'close','open']

        super(fac_2, self).__init__(required_columns=required_columns
                                  )
        
    
    def on_bar(self, i_data, a = 10, b = 10,c = 60):
        spot_o = i_data['open']
        spot_h = i_data['high']
        spot_l = i_data['low']
        spot_c = i_data['close']
        
        def calc_overlining_std(c,o,h,l,window):
            if_up = (c-o>0)*1
            up_overlining = ((h-c)* if_up).ewm(span = window).std()
            return (up_overlining)/r((h-l).ewm(span = window).mean())


        def calc_underlining_std(c,o,h,l,window):
            if_down = (c-o<0)*1
            down_underlining = ((c-l)* if_down).ewm(span = window).std()
            return (down_underlining)/r((h-l).ewm(span = window).mean())
        
        overlining_std = calc_overlining_std(spot_c,spot_o, spot_h, spot_l,a)
        underlining_std = calc_underlining_std(spot_c,spot_o, spot_h, spot_l,b)
        underlining_std_norm = ts_rank(underlining_std, 300 * c)
        factor = ts_rank(underlining_std-overlining_std, 300 * c).to_frame()
        factor.columns = [self.__class__.__name__]
        return factor
