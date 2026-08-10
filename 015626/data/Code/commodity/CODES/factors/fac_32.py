import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *
# MM_ZF
class fac_32(FactorGenerator):
    def __init__(self):
        required_columns=['close']

        super(fac_32, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):
        sig = data['close']
        sig = rolling_norm(sig, aa)
        sig = sig.ewm(bb, min_periods=1).mean()
        sig.name = self.__class__.__name__
        if ccc >= 60:
            return pd.DataFrame(sig)
        else:
            return ts_rank(pd.DataFrame(sig), ccc * 300)