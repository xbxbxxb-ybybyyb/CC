import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
from operators_cc import *
import pandas as pd
    
class fac_4(FactorGenerator):
    def __init__(self):
        required_columns=['high', 'low', 'close','open']

        super(fac_4, self).__init__(required_columns=required_columns
                                  )
        
    
    def on_bar(self, i_data, aaa = 5, bbb = 10 ,ccc= 60, ddd = 10):
        spot_o = i_data['open']
        spot_h = i_data['high']
        spot_l = i_data['low']
        spot_c = i_data['close']
        
        def calc_slope(val, window):
            x = np.cumsum(np.ones(shape=window))
            def calc_slope_in_window(target):
                return np.cov(x,target)[0,1]
            return val.rolling(window).apply(calc_slope_in_window)

        def calc_ma_slope(c,window_ma, window_slope):
            ma = c.rolling(window_ma).mean()
            return calc_slope(ma, window_slope)

        ma_slope_15 = calc_ma_slope(spot_c,aaa, bbb)
        ma_slope_60 = calc_ma_slope(spot_c,aaa, ccc)
        ma_slope_fac = ma_slope_15 + ma_slope_60
        #ma_slope_fac = ma_slope_60
        factor = ts_rank(ma_slope_fac, ddd * 300).to_frame()
        factor.columns = [self.__class__.__name__]
        return factor