
# coding: utf-8

# In[ ]:

from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_wsc_for_srch import *

class wsc_hf_15_srch_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_smallorder_money','sell_smallorder_money_v2','buy_bigorder_money','sell_bigorder_money_v2', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = None


    def calculate(self, df):
        
        a = df['buy_smallorder_money'].values[-15:]
        b = df['sell_smallorder_money_v2'].values[-15:]
        c = df['buy_bigorder_money'].values[-15:]
        d = df['sell_bigorder_money_v2'].values[-15:]
        w = df['weight'].values[-15:]
        
        bba_4_r = np.nansum(a, axis = 1) / np.nansum(replace_zero(a+b), axis = 1)
        bba_2_r_w = np.nansum(c / replace_zero(c+d) * w, axis =1)

        
        factor = bba_4_r - bba_2_r_w + midpoint(bba_4_r, 15)
        return -factor[-1]

