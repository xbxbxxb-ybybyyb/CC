import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *

# ret_sharpe
class fac_37(FactorGenerator):
    def __init__(self):
        required_columns=['close']

        super(fac_37, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):
        ##### def data #####
        close = data['close']
        minute_ret = close - close.shift(int(np.floor((np.sqrt(aa))/2)))

        ##### calc factor #####
        min_pct = 0.7
        sharpe_win = bb
        ts_pct_win = ccc * 300
        ret_sharpe_raw = minute_ret.rolling(sharpe_win).mean() / r(minute_ret.rolling(sharpe_win).std())
        ret_sharpe = ts_rank(ret_sharpe_raw, ts_pct_win)

        factor = pd.DataFrame(ret_sharpe)
        factor.columns = [self.__class__.__name__]
        
        return factor
