
# coding: utf-8

# In[ ]:


from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_all_wsc import *

class cf_search11_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_smallorder_money','sell_smallorder_money_v2','buy_bigorder_money','sell_bigorder_money_v2', 'SellTradeNum', 'SellTradeMoney', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = None


    def calculate(self, df):
        
        a = df['buy_smallorder_money'].values[-180:]
        b = df['sell_smallorder_money_v2'].values[-180:]
        c = df['buy_bigorder_money'].values[-180:]
        d = df['sell_bigorder_money_v2'].values[-180:]
        e = df['SellTradeNum'].values[-180:]
        f = df['SellTradeMoney'].values[-180:]
        w = df['weight'].values[-180:]
        
        bba_4_r = np.nansum(a, axis = 1) / np.nansum(replace_zero(a+b), axis = 1)
        bba_2_r_w = np.nansum(c / replace_zero(c+d) * w, axis =1)
        sa_to_sn = np.nansum(f, axis = 1) / np.nansum(replace_zero(e), axis = 1)
        
        factor = -midprice(midprice(sub2(bba_4_r, bba_2_r_w), auto_corr(sa_to_sn, 70, 90), 10), bba_4_r, 10)
        return factor[-1]

