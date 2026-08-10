import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *

# hhll_ind_CC
class fac_28(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'high', 'low']

        super(fac_28, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc, dd):

        temp = np.where((data['high']>data['high'].shift(1)) & (data['low']>data['low'].shift(1)), int(np.sqrt(aa)), np.where((data['high']<data['high'].shift(1)) & (data['low']<data['low'].shift(1)), 0, int(np.sqrt(np.sqrt(bb)))))
        temp = pd.Series(temp, index = data['high'].index)
        vwtc_r = temp.ewm(ccc, min_periods =1).mean()
        factor = vwtc_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, dd * 300)

        return factor