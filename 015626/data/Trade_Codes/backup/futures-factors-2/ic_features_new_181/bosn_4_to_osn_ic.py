
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *

class bosn_4_to_osn_ic(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_small_lo_counts', 'sell_lo_counts']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = False


    def calculate(self, df):
        
        a = df['sell_small_lo_counts'].values[-1]
        b = df['sell_lo_counts'].values[-1]

        
        factor = np.nansum(a) / np.nansum(b)
        return factor

