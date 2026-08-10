import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
from operators_cc import *
import pandas as pd

class fac_21(FactorGenerator):
    def __init__(self):
        required_columns=['high', 'low', 'close','open']

        super(fac_21, self).__init__(required_columns=required_columns
                                  )
        
    
    def on_bar(self, data, aa, bb, ccc):

        temp = np.abs(data['close'] - data['open'])
        temp[temp == 0] = 0.1
        temp0 = (data['high'] - data['low'])
        temp1 = temp0/temp
        a = (data['close'] - data['close'].shift(1)).rolling(aa, min_periods = 1).sum()
        vwtc_r = (temp1*(a)).rolling(bb, min_periods = 1).mean()
        factor = vwtc_r.to_frame()

        factor.columns = [self.__class__.__name__]

        factor = ts_rank(factor, ccc * 300)

        return factor
