import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *

class cf_search8_ih(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_smallorder_money','sell_smallorder_money_v2','BuyUniqueOrderNum','SellUniqueOrderNum', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = None


    def calculate(self, df):
        
        a = df['buy_smallorder_money'].values[-200:]
        b = df['sell_smallorder_money_v2'].values[-200:]
        c = df['BuyUniqueOrderNum'].values[-200:]
        d = df['SellUniqueOrderNum'].values[-200:]
        w = df['weight'].values[-200:]
        
        bba_4_r_w = np.nansum(a/replace_zero(a+b)*w, axis=1)
        bun_r = np.nansum(c, axis =1) / replace_zero(np.nansum((c+d), axis=1))
        
        factor = -dema(add2(bun_r, ts_reg_alpha(ts_max(bba_4_r_w, 100), 90)), 10)
        return factor[-1]

