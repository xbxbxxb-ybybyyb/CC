import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *


#GA_ind_CC
class fac_23(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'high', 'low', 'open']

        super(fac_23, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb):
        n = aa
        a = data['high'].rolling(n, min_periods = int(n/2)).max()-data['open'].shift(n)
        b = data['close'] - data['low'].rolling(n, min_periods = int(n/2)).min()
        c = (data['high'].rolling(n, min_periods = int(n/2)).max()-data['low'].rolling(n, min_periods = int(n/2)).min())*2
        vwtc_r = (a*b)/c
        factor = vwtc_r.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, bb * 300)
        factor = pd.DataFrame(factor)
        return factor