import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
from operators_cc import *
import pandas as pd

class fac_5(FactorGenerator):
    def __init__(self):
        required_columns=['high', 'low', 'close','open']

        super(fac_5, self).__init__(required_columns=required_columns
                                  )
        
    def on_bar(self, i_data, aaa = 60, bbb = 240 ,ccc = 20):



        spot_o = i_data['open']
        spot_h = i_data['high']
        spot_l = i_data['low']
        spot_c = i_data['close']


        def calc_overlining_inc(c,o,h,l,window):
            box_top = c.where(c>o,o)
            overlining = (h-box_top)
            overlining_diff = overlining - overlining.shift(1).rolling(aaa).mean() 
            overlining_inc = overlining_diff.where(overlining_diff>0,0)
            return overlining_inc.ewm(span=window).mean()/r((h-l).ewm(span=window).mean())

        def calc_underlining_inc(c,o,h,l,window):
            box_bottom = c.where(c<o,o)
            underlining = (box_bottom-l)
            underlining_diff = underlining - underlining.shift(1).rolling(aaa).mean() 
            underlining_inc = underlining_diff.where(underlining_diff>0,0)
            return underlining_inc.ewm(span=window).mean()/r((h-l).ewm(span=window).mean())

        overlining_inc = calc_overlining_inc(spot_c,spot_o,spot_h,spot_l,bbb)
        underlining_inc = calc_underlining_inc(spot_c,spot_o,spot_h,spot_l,bbb)
        fac = ts_rank(underlining_inc-overlining_inc, ccc * 240).to_frame()
        fac.columns = [self.__class__.__name__]
        return fac