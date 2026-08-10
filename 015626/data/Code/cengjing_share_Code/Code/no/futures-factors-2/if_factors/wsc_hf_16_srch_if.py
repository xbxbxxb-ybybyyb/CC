from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_wsc_for_srch import *

class wsc_hf_16_srch_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_smallorder_money','sell_smallorder_money_v2','BuyUniqueOrderNum','BuyTradeNum', 'SellTradeNum','weight']
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
        w = df['weight'].values[-170:]
        
        bba_4_r = np.nansum(a, axis = 1) / np.nansum(replace_zero(a+b), axis = 1)
        bun_to_bn_w = np.nansum(c / replace_zero(d) * w, axis =1)
        bn_r = np.nansum(d, axis = 1) / np.nansum(replace_zero(d+e), axis = 1)

        
        factor = add2(ts_rank(add2(midpoint(bba_4_r, 15), bun_to_bn_w), 120), ts_skew(bn_r, 25))
        return -factor[-1]

