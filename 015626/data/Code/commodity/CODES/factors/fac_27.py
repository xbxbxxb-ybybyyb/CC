import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *

# LMLS
class fac_27(FactorGenerator):
    def __init__(self):
        required_columns=[ 'low']

        super(fac_27, self).__init__(required_columns=required_columns
                                  )
        
    def on_bar(self, data, aa, bb, ccc):
        if bb < 100:
            bb_temp = int(aa * bb / 100)
        elif (bb > 100) and (bb < 200):
            bb_temp = int(aa / 3)
        else:
            bb_temp = int(aa * 2 / 3)

        temp = data['low'].rolling(aa, min_periods = 1).mean() - data['low'].shift(bb_temp).rolling(aa - bb_temp, min_periods = 1).mean()
        factor = temp.to_frame()

        factor.columns = [self.__class__.__name__]

        factor = ts_rank(factor, ccc * 300)

        return factor
