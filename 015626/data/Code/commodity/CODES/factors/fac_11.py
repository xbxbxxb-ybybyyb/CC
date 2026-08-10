import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import ts_rank, r
from utils_zsj import *
#tr1
class fac_11(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'high', 'low']

        super(fac_11, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc):
        hh = data['high'].rolling(aaa, min_periods=1).max()
        ll = data['low'].rolling(bbb, min_periods=1).min()
        sig = 2 * data['close'] / r(hh + ll)
        sig = ts_rank(sig, 300 * ccc)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
