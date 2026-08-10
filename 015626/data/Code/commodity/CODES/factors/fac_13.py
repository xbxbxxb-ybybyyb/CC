import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import ts_rank, r
from utils_zsj import *

#LminLmean
class fac_13(FactorGenerator):
    def __init__(self):
        required_columns=['low']

        super(fac_13, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc):
        future_low = data['low']
        
        ctl_r = future_low.rolling(aaa, min_periods = 1).mean() / r(future_low.rolling(bbb, min_periods = 1).mean())
        factor = ts_rank(ctl_r, ccc * 300).to_frame()
        factor.columns = [self.__class__.__name__]
        return -factor