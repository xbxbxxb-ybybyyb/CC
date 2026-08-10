import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *

#CDO_ind
class fac_20(FactorGenerator):
    def __init__(self):
        required_columns=['close',  'volume']

        super(fac_20, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):
        ##### def data #####


        ##### calc factor #####
        df = pd.concat( [data['volume'], data['close']], axis = 1) 
        df_corr = -df.rolling(aa, min_periods = 1).corr(pairwise=True).unstack()
        df_corr = df_corr[('volume', 'close')]
        df_corr[df_corr == np.inf] = np.nan
        
        
        close_volume_corr_change = df_corr.rolling(bb, min_periods = 1).mean()
        
        ##### format factor #####
        close_volume_corr_change.name = self.__class__.__name__
        factor = pd.DataFrame(close_volume_corr_change)
        factor = ts_rank(factor, ccc*300)
        #factor[factor<=-0.5] = np.nan
        return factor