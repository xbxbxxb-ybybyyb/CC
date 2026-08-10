
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *

class bosa_2_to_osa_w_ic(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_big_lo_amount', 'sell_lo_amount', 'weight']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = False


    def calculate(self, df):
        
        a = df['sell_big_lo_amount'].values[-1]
        b = df['sell_lo_amount'].values[-1]
        w = df['weight'].values[-1]

        
        factor = np.nansum(a / b * w)
        return factor

