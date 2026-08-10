from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_all_wsc import *

class search5_wyc(FutureFactor):
#     factor = sub2(long_short_ma_ratio(ba_to_bn_w, 40, 120), bun_to_bn_w)
#     factor = ts_mean(factor, 2)
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum','weight','BuyTradeMoney']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    
    def calculate(self, df):        
        ba_to_bn_w = ((df['BuyTradeMoney'][-122:] / df['BuyTradeNum'][-122:]) * df['weight'][-122:]).sum(axis = 1)
        bun_to_bn_w = ((df['BuyUniqueOrderNum'][-2:] / df['BuyTradeNum'][-2:].replace(0, np.nan)) * df['weight'][-2:]).sum(axis = 1).values
        _b = long_short_ma_ratio(ba_to_bn_w, 40, 120)[-2:].values
        return np.nanmean(_b - bun_to_bn_w)