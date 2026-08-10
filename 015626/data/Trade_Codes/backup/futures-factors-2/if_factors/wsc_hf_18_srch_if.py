
# coding: utf-8

# In[ ]:


from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_wsc_for_srch import *

class wsc_hf_18_srch_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_smallorder_money','sell_smallorder_money_v2','BuyTradeMoney', 'SellTradeMoney','sell_superorder_count_v2','SellUniqueOrderNum','buy_bigorder_money', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = None


    def calculate(self, df):
        
        a = df['buy_smallorder_money'].values[-190:]
        b = df['sell_smallorder_money_v2'].values[-190:]
        d = df['BuyTradeMoney'].values[-190:]
        e = df['SellTradeMoney'].values[-190:]
        f = df['sell_superorder_count_v2'].values[-190:]
        g = df['SellUniqueOrderNum'].values[-190:]
        h = df['buy_bigorder_money'].values[-190:]
        w = df['weight'].values[-190:]
        
        sba_4_to_sa = np.nansum(b, axis = 1) / np.nansum(replace_zero(e), axis = 1)
        sbn_1_to_sun_w = np.nansum(f / replace_zero(g) * w, axis = 1)
        bba_4_r_w = np.nansum(a / replace_zero(a+b) * w, axis = 1)
        bba_2_to_ba = np.nansum(h, axis = 1) / np.nansum(replace_zero(d), axis = 1)
        

        
        factor = mul2(div2(mul2(sba_4_to_sa, ts_pred(cross_hub_num(sbn_1_to_sun_w, 100), 90)), bba_4_r_w), bba_2_to_ba)
        return factor[-1]

