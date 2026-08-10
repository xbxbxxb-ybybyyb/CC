import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from rolling_adj import *


def rolling_normalize(sig, window=100):
    sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
    sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
    return ((sig - sig_min) / (sig_max - sig_min)) * 2 - 1


# tr1_zf
class fac_42_5min_df_5x_noroll_(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high', 'close', 'main_mask']

        super(fac_42_5min_df_5x_noroll_, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc):

        mask = data['main_mask']
        coef = int(np.nanmedian(mask.groupby(mask.index.date).count()))
        w1 = int(coef * aaa / 5)
        w2 = int(coef)
        w3 = int(coef * aaa * 5)
        
        hh = data['high'].rolling(w1, min_periods=1).max()
        ll = data['low'].rolling(w1, min_periods=1).min()
        sig1 = (2 * data['close'] / (hh + ll))[mask].mean(axis = 1)
        
        hh = data['high'].rolling(w2, min_periods=1).max()
        ll = data['low'].rolling(w2, min_periods=1).min()
        sig2 = (2 * data['close'] / (hh + ll))[mask].mean(axis = 1)
        
        hh = data['high'].rolling(w3, min_periods=1).max()
        ll = data['low'].rolling(w3, min_periods=1).min()
        sig3 = (2 * data['close'] / (hh + ll))[mask].mean(axis = 1)
        
        sig = (sig1 +  sig2 + sig3 * 2)
        
        vol = data['close'].rolling(w2, min_periods = 2).std()[mask].mean(axis = 1)
        sig = sig.ewm(bbb, min_periods = 1).mean() + sig
        sig = ts_rank(sig, 300 * ccc)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)