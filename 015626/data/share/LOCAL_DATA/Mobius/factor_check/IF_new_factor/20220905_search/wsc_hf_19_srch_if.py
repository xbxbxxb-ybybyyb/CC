from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_all_wsc import *

class wsc_hf_19_srch_if(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_bigorder_count_v2','SellUniqueOrderNum','weight','BuyTradeNum','SellTradeNum','BuyUniqueOrderNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.75,1]'
    handle_preadj = None 

    def calculate(self, df):
        
        sbn_2_to_sun_w = (df['sell_bigorder_count_v2'] / df['SellUniqueOrderNum'] * df['weight']).sum(axis = 1)[-121:]
        bn_r_w = (df['BuyTradeNum'] / (df['BuyTradeNum'] + df['SellTradeNum']) * df['weight']).sum(axis = 1)[-11:]
        bun_to_bn_w = ((df['BuyUniqueOrderNum'][-1:] / df['BuyTradeNum'][-1:]) * df['weight'][-1:]).sum(axis = 1).values[-1]

        x1 = sigmoid(ts_skew(sbn_2_to_sun_w, 110))[-11:]
        x2 = midprice(bn_r_w, x1, 10).values[-1]
        factor = np.add(x2, bun_to_bn_w) * -1
        
        return factor