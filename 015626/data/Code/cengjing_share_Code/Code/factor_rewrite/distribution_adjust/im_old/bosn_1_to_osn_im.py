
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *

class bosn_1_to_osn_im(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_super_lo_counts', 'sell_lo_counts']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = False


    def calculate(self, df):
        
        a = df['sell_super_lo_counts'].values[-1]
        b = df['sell_lo_counts'].values[-1]

        
        factor = np.nansum(a) / np.nansum(b)
        return np.log(factor) if factor > 0 else np.nan

