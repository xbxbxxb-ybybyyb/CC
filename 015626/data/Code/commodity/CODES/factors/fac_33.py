import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *
# OcorrC
class fac_33(FactorGenerator):
    def __init__(self):
        required_columns=['close']

        super(fac_33, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, ccc):

        t_occor2 = data['open'].rolling(aa, min_periods = 1).corr(data['close'])


        t_occor2[t_occor2 == np.inf] = 1       
        factor = t_occor2 * (data['close'] - data['open']).ewm(aa, min_periods = 1).mean()

        
        factor = ts_rank(factor, ccc * 300).to_frame()
        
        factor.columns = [self.__class__.__name__]
        return factor