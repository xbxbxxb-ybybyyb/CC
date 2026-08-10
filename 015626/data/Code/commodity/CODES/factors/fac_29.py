import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *
# HLDL2_ind_CC_IF
class fac_29(FactorGenerator):
    def __init__(self):

        required_columns =['high', 'low']

        super(fac_29, self).__init__(
                                  required_columns=required_columns)

    def on_bar(self, data, aaa, bbb):


        t_pcorr = (data['high'].diff()+data['low'].diff()).rolling(aaa, min_periods = 1).mean()
        factor = t_pcorr.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, bbb * 300)

        return factor
