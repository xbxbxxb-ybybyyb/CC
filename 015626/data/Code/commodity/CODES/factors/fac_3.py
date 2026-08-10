import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *
    
class fac_3(FactorGenerator):
    def __init__(self):
        required_columns=['high', 'low', 'close','open']

        super(fac_3, self).__init__(required_columns=required_columns
                                  )
        
    
    def on_bar(self, i_data, aaa = 1, bbb = 1, ccc = 1,  ddd = 1):
        spot_o = i_data['open']
        spot_h = i_data['high']
        spot_l = i_data['low']
        spot_c = i_data['close']
        
        def calc_exceeding_length(c,o,h,l, window):
            box_top = c.where(c>o,o)
            box_bot = c.where(c<o,o)
            non_covered_up = np.maximum(c-h.shift(1),0)/r(h-l)
            non_covered_down = np.maximum(l.shift(1)-c,0)/r(h-l)
            avg_gain = non_covered_up.ewm(span = window).mean()
            avg_loss = non_covered_down.ewm(span = window).mean()
            exceeding_length_rsi = (avg_gain/r(avg_gain + avg_loss))*100
            return exceeding_length_rsi.ewm(span=aaa).mean()

        exceeding_length_rsi = calc_exceeding_length(spot_c,spot_o, spot_h,spot_l,bbb).rolling(ccc).mean()
        factor = ts_rank(exceeding_length_rsi, ddd * 240).to_frame()
        factor.columns = [self.__class__.__name__]
        return factor