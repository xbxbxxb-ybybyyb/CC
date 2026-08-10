import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *

# ss1_zf
class fac_48_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'high', 'second_main_mask']

        super(fac_48_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc, ddd):
        aaa = 3
        bbb = 120
        ccc = 120
        ddd = 20
        mask = data['second_main_mask']
        rtn = data['close'] - data['close'].shift(aaa)
        vol = rtn.rolling(bbb, min_periods=1).std()
        vol[vol < 1e-8] = np.nan
        ret = data['close'] - (data['high'].shift(aaa).rolling(bbb, min_periods=1).max()) - 1
        sig = ((ret / r(vol)).rolling(int(np.sqrt(ccc) - 1), min_periods = 1).mean())[mask].mean(axis = 1)
        sig = ts_rank(sig, 300 * ddd)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
