import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
from operators_cc import *
import pandas as pd

class fac_6(FactorGenerator):
    def __init__(self):
        required_columns=['high', 'low', 'close','open']

        super(fac_6, self).__init__(required_columns=required_columns
                                  )
        
    
    def on_bar(self, i_data, aaa = 40, bbb = 10):
        spot_o = i_data['open']
        spot_h = i_data['high']
        spot_l = i_data['low']
        spot_c = i_data['close']
        
        def calculate_line_rsi(c,o,h,l,window):
    
            box_top = c.where(c>o,o)
            box_bot = c.where(c<o,o)
            line_diff = ((box_bot-l) - (h-box_top))/r(h-l).ewm(span=window).mean()
            gain = line_diff.where(line_diff>0,0)
            loss = -line_diff.where(line_diff<0,0)
            avg_gain = gain.ewm(span = window).mean()
            avg_loss = loss.ewm(span = window).mean()
            line_rsi = (avg_gain/ r(avg_loss + avg_gain))
            return line_rsi 

        line_rsi  = calculate_line_rsi(spot_c,spot_o,spot_h,spot_l,aaa)
        fac = ts_rank(line_rsi, bbb * 240).to_frame()
        fac.columns = [self.__class__.__name__]
        return fac