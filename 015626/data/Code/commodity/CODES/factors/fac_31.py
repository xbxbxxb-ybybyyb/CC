import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *

# LSC
class fac_31(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'low', 'high']

        super(fac_31, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):

        hh = (data['high'].rolling(aa, min_periods = 1).max() - data['close'])/r(data['high'].rolling(aa, min_periods = 1).max() - data['low'].rolling(aa, min_periods = 1).min()) 
        ll = (data['close'] - data['low'].rolling(aa, min_periods = 1).min())/r(data['high'].rolling(aa, min_periods = 1).max() - data['low'].rolling(aa, min_periods = 1).min())
        vwtc_r = ll.rolling(bb, min_periods = 1).mean()-hh.rolling(bb, min_periods = 1).mean()
        factor = vwtc_r.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, ccc * 300)

        return factor