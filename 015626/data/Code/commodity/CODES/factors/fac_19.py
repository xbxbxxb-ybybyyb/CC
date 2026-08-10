import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *

#CDO_ind
class fac_19(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'open']

        super(fac_19, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):

        cdo_r = data['close'].rolling(aa, min_periods = 1).mean()-data['open'].rolling(aa, min_periods = 1).mean()
        factor = cdo_r.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = factor.ewm(int(np.sqrt(bb)),min_periods=1).mean()
        factor = ts_rank(factor, ccc * 300)
        

        return factor