import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *


def rolling_normalize(sig, window=100):
    sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
    sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
    return ((sig - sig_min) / (sig_max - sig_min)) * 2 - 1


# tr1_zf
class fac_42_df_5x_(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high', 'close', 'main_mask']

        super(fac_42_df_5x_, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc):
 
        mask = data['main_mask']
        coef = int(np.nanmedian(mask.groupby(mask.index.date).count()))
        w1 = int(coef * aaa / 10)
        w2 = int(coef)
        w3 = int(coef * aaa * 5)
        
        hh = data['high'].rolling(w1, min_periods=1).max()
        ll = data['low'].rolling(w1, min_periods=1).min()
        sig1 = (2 * data['close'] / (hh + ll))[mask].mean(axis = 1)
        
        hh = data['high'].rolling(w3, min_periods=1).max()
        ll = data['low'].rolling(w3, min_periods=1).min()
        sig3 = (2 * data['close'] / (hh + ll))[mask].mean(axis = 1)
        
        sig = (sig1 * 2 + sig3)
        

        sig = sig.rolling(bbb , min_periods = 1).mean() 
        sig = ts_rank(sig, coef * ccc)
        
        hclose = data['close'][mask].mean(axis = 1)
        coef = int(np.nanmedian(mask.groupby(mask.index.date).count()))
        cs = sig.rolling(int(coef), min_periods = 2).corr(hclose)
        cl = sig.rolling(int(coef * 3) ,min_periods = 2).corr(hclose)
        sig[(cs <cl) | (cl < 0)] = 0
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)