import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *

# ERET_CC_IF
class fac_30(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'low']

        super(fac_30, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, ccc):

        lltc_ind_r = -data['low'].rolling(aa, min_periods = int(aa/2)).min()/(data['close'])
        factor = lltc_ind_r.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, ccc * 300)

        return factor