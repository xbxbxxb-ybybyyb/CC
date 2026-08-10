import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *

# OCtHL
class fac_34(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'open', 'high', 'low']

        super(fac_34, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):

        temp1 = data['open'] - data['close']
        temp2 = data['high'] - data['low']
        t_pcor2 = -temp1/r(temp2)
        t_pcor2[t_pcor2 == np.inf] = 0
        t_pcor2 = t_pcor2.rolling(aa, min_periods = 1).mean().ewm(int(np.sqrt(bb)), min_periods = 1).mean()
        factor = t_pcor2.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, ccc * 300)

        return factor