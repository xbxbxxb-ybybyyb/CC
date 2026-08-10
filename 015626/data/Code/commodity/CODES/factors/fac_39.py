import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *

# sr1_zf
class fac_39(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'low']

        super(fac_39, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):
        rtn = data['close'] - data['close'].shift(1) 
        vol = rtn.rolling(aa, min_periods=1).std()
        ret = data['close'] - (data['low'].shift(1).rolling(aa, min_periods=1).min()) 
        sig = (ret / r(vol)).ewm(int(np.sqrt(bb))).mean()
        sig = ts_rank(sig, 300 * ccc)

        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
