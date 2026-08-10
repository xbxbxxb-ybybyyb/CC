import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import ts_rank, r
from utils_zsj import *


class fac_9(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'high']

        super(fac_9, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc):
        rtn = data['close'] - data['close'].shift(1)
        vol = rtn.rolling(aaa, min_periods=1).std()
        ret =  (data['high'].shift(1).rolling(aaa, min_periods=1).max()) - data['close']
        sig = (ret / r(vol)).ewm(bbb).mean()
        sig = ts_rank(sig, 300 * ccc)


        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
