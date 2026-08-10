import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *

# ret_sharpe
class fac_37_orig_1min_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'main_mask']

        super(fac_37_orig_1min_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):
        aa = 15
        bb = 240
        ccc = 3
        ##### def data #####
        close = (data['close'])
        mask = data['main_mask']
        coef = int(np.nanmedian(mask.groupby(mask.index.date).count()))
        
        minute_ret = (close - close.shift(15))[mask].mean(axis = 1)

        ##### calc factor #####
        min_pct = 0.7
        sharpe_win = int(coef / 2)
               
        ts_pct_win = int(ccc * 300)
        temp1 = minute_ret.rolling(sharpe_win).mean()
        temp2 = minute_ret.rolling(sharpe_win).median()
        temp = (temp1 * 2 + temp2)
        ret_sharpe_raw = temp / r(minute_ret.rolling(int(sharpe_win/2)).std())
        ret_sharpe_raw = ret_sharpe_raw.rolling(3, min_periods=  1).mean()
        ret_sharpe = ts_rank(ret_sharpe_raw, ts_pct_win)

        factor = pd.DataFrame(ret_sharpe)
        factor.columns = [self.__class__.__name__]
        
        return factor
