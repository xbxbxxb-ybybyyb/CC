import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *

# ret_sharpe
class fac_37_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'main_mask', 'volume']

        super(fac_37_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):
        aa = 3
        bb = 120
        ccc = 3
        ##### def data #####
        close = (data['close'])
        mask = data['main_mask']
        volume = data['volume']      
        minute_ret = (close - close.shift(aa))[mask].mean(axis = 1)

        ##### calc factor #####
        min_pct = 0.7
        sharpe_win = bb
               
        ts_pct_win = int(ccc * 300)
        temp1 = minute_ret.rolling(sharpe_win).mean()
        temp2 = minute_ret.rolling(sharpe_win).median()
        temp = (temp1 * 2 + temp2)
        ret_sharpe_raw = temp / r(minute_ret.rolling(int(sharpe_win/2), min_periods = 1).std()) / r(volume.rolling(int(sharpe_win), min_periods = 1).sum()[mask].mean(axis = 1))
        ret_sharpe = ts_rank(ret_sharpe_raw, ts_pct_win)

        factor = pd.DataFrame(ret_sharpe)
        factor.columns = [self.__class__.__name__]
        
        return factor
