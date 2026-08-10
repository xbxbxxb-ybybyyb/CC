import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import ts_rank, r
from utils_zsj import *
# wsc_spot_38_if
class fac_12(FactorGenerator):
    def __init__(self):
        required_columns=['close']

        super(fac_12, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc):
        spot_close_if = data['close']
        
        factor_raw = np.sign(ts_pct_change(spot_close_if, 1)) * ts_sum((ts_pct_change(spot_close_if, 1) ** 2), aaa)
        factor = factor_raw.rolling(bbb, min_periods = 1).mean()
        factor = ts_rank(factor, 300 * ccc)
        factor.name = self.__class__.__name__
        return factor.to_frame()
