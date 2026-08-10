import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
from operators_cc import *
import pandas as pd

class fac_7(FactorGenerator):
    def __init__(self):
        required_columns=['high', 'low', 'close','open']

        super(fac_7, self).__init__(required_columns=required_columns
                                  )
    
            
    def on_bar(self, i_data, aaa = 50, bbb = 5, ccc = 20):

        spot_o = i_data['open']
        spot_h = i_data['high']
        spot_l = i_data['low']
        spot_c = i_data['close']


        def calc_distance_to_high(c,window):
            return c/c.rolling(window).max() - 1

        def calc_distance_to_low(c,window):
            return c/c.rolling(window).min() - 1

        distance_to_high = calc_distance_to_high(spot_c,aaa).ewm(span=bbb).mean()
        distance_to_low = calc_distance_to_low(spot_c,aaa).ewm(span=bbb).mean()
        factor = ts_rank(distance_to_high+distance_to_low, ccc * 240).to_frame()
        factor.columns = [self.__class__.__name__]
        return factor