import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *

# OCtHL
class fac_34_orig_1min_df_10x_(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'open', 'high', 'low', 'main_mask']

        super(fac_34_orig_1min_df_10x_, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):
        aa = 50
        bb = 450
        ccc = 30
        mask = data['main_mask']
        #second_mask = data['second_main_mask']
        #weight = data['amount'].div(data['amount'].sum(axis = 1), axis = 0)

        coef = int(np.nanmedian(mask.groupby(mask.index.date).count()))
        
        temp1 = data['open'].rolling(aa, min_periods = 1).mean() - data['close']#.rolling(5, min_periods = 1).mean()
        temp2 = data['high'].rolling(aa, min_periods = 1).max()  - data['low'].rolling(aa, min_periods = 1).min() 
        t_pcor2 = (-temp1/r(temp2))[mask].mean(axis = 1)
        t_pcor2[t_pcor2 == np.inf] = 0
        fac = t_pcor2.ewm(bb, min_periods = 1).mean()

        
        factor = ts_rank(fac, coef * ccc).to_frame()
        factor.columns = [self.__class__.__name__]
        return factor