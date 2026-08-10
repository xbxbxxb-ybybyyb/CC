import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *

# 
class fac_16(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high']

        super(fac_16, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb):
        spot_h = data['high']
        spot_l = data['low']
        ctl_r = spot_h.rolling(aaa, min_periods = 1).corr(spot_l)
        factor = ts_rank(ctl_r, bbb * 300).to_frame()
        factor.columns = [self.__class__.__name__]
        return factor
