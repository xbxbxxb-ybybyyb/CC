import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *

# MinuteLongTermRtn_IF
class fac_26(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'high', 'low']

        super(fac_26, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):

        hclose = data['close']
        hhigh = data['high']
        hlow = data['low']
        index_typical = hclose + hhigh + hlow
        index_typical_r = (index_typical.diff()) / index_typical.shift(1)
        
        factor = index_typical_r.ewm(aa, min_periods = 1).mean() / r(np.abs(index_typical_r).ewm(bb, min_periods = 1).mean())
        factor = ts_rank(factor, ccc * 300).to_frame()
        factor.columns = [self.__class__.__name__]
        return factor