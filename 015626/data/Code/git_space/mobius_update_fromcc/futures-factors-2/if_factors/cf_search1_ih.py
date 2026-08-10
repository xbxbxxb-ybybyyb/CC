import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class cf_search1_ih(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_smallorder_money','sell_smallorder_money_v2','BuyUniqueOrderNum','SellUniqueOrderNum', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = None


    def calculate(self, df):
        
        a = df['BuyUniqueOrderNum'].values[-25:]
        b = df['SellUniqueOrderNum'].values[-25:]
        c = df['buy_smallorder_money'].values[-25:]
        d = df['sell_smallorder_money_v2'].values[-25:]
        w = df['weight'].values[-25:]
        
        bun_r_w = np.nansum(a / replace_zero(a + b) * w, axis=1)
        bba_4_r = np.nansum(c, axis=1) / replace_zero(np.nansum((c + d), axis=1))
        
        
        factor = -midprice(bun_r_w, ts_max(bba_4_r, 20), 5)
        return factor[-1]

