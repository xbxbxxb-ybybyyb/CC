
# coding: utf-8

# In[ ]:

from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_all_wsc import *

class cf_search10_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_smallorder_money','sell_smallorder_money_v2','BuyUniqueOrderNum','SellUniqueOrderNum', 'BuyTradeNum', 'BuyTradeMoney', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = None


    def calculate(self, df):
        
        a = df['buy_smallorder_money'].values[-60:]
        b = df['sell_smallorder_money_v2'].values[-60:]
        c = df['BuyUniqueOrderNum'].values[-60:]
        d = df['SellUniqueOrderNum'].values[-60:]
        e = df['BuyTradeNum'].values[-60:]
        f = df['BuyTradeMoney'].values[-60:]
        w = df['weight'].values[-60:]
        
        bba_4_r = np.nansum(a, axis = 1) / np.nansum(replace_zero(a+b), axis=1)
        bun_to_bn_w = np.nansum(c / replace_zero(e) * w, axis =1)
        ba_to_bn_w = np.nansum(f / replace_zero(e) * w, axis =1)
        bba_4 = np.nansum(a, axis = 1)
        
        factor = -midprice(bba_4_r, midprice(bun_to_bn_w, ts_corr(ba_to_bn_w, bba_4, 30), 15), 15)
        return factor[-1]

