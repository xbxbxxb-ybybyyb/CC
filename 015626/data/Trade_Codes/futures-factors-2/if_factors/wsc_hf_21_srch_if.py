from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_wsc_for_srch import *

class wsc_hf_21_srch_if(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum','sell_bigorder_count_v2','weight','SellUniqueOrderNum','BuyTradeMoney','SellTradeMoney','BuyUniqueOrderNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.75,1]'
    handle_preadj = None 

    def calculate(self, df):
        bun_to_bn_w = ((df['BuyUniqueOrderNum'][-1:] / df['BuyTradeNum'][-1:]) * df['weight'][-1:]).sum(axis = 1).values[-1]
        sbn_2_to_sun = df['sell_bigorder_count_v2'][-21:].sum(axis = 1) / df['SellUniqueOrderNum'][-21:].sum(axis = 1)
        ba_r_w = (df['BuyTradeMoney'][-21:] / (df['BuyTradeMoney'][-21:] + df['SellTradeMoney'][-21:]) * df['weight'][-21:]).sum(axis = 1)
        factor = bun_to_bn_w * midprice(ba_r_w, sbn_2_to_sun, 20).values[-1] * -1
        return factor