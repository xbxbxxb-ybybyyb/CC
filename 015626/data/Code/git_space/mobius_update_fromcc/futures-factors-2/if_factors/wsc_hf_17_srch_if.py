
# coding: utf-8

# In[ ]:


from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_wsc_for_srch import *

class wsc_hf_17_srch_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_smallorder_money','sell_smallorder_money_v2','BuyUniqueOrderNum','BuyTradeNum', 'SellTradeNum','sell_bigorder_count_v2','SellUniqueOrderNum','buy_smallorder_count', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = None


    def calculate(self, df):
        
        a = df['buy_smallorder_money'].values[-170:]
        b = df['sell_smallorder_money_v2'].values[-170:]
        c = df['BuyUniqueOrderNum'].values[-170:]
        d = df['BuyTradeNum'].values[-170:]
        e = df['SellTradeNum'].values[-170:]
        f = df['sell_bigorder_count_v2'].values[-170:]
        g = df['SellUniqueOrderNum'].values[-170:]
        h = df['buy_smallorder_count'].values[-170:]
        w = df['weight'].values[-170:]
        
        bbn_4_to_bun = np.nansum(h, axis = 1) / np.nansum(replace_zero(c), axis = 1)
        bba_4_r = np.nansum(a, axis = 1) / np.nansum(replace_zero(a+b), axis = 1)
        sbn_2_to_sun_w = np.nansum(f / replace_zero(g) * w, axis =1)
        bn_r_w = np.nansum(d / replace_zero(d+e) * w, axis = 1)

        
        factor = add2(add2(mul2(bbn_4_to_bun, ts_sum(bba_4_r, 20)), ts_skew(sbn_2_to_sun_w, 100)), ts_skew(bn_r_w, 20))
        return -factor[-1]

