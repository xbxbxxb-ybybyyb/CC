from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_all_wsc import *

class search11_wyc_IM(FutureFactor):
#     factor = div2(ts_pred(rsi(sa_to_sn_w, 50), 50), bun_to_bn_w)
#     factor = ts_mean(factor, 2)
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['SellTradeMoney', 'SellTradeNum','BuyUniqueOrderNum','BuyTradeNum','weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    
    def calculate(self, df):        
        sa_to_sn_w = ((df['SellTradeMoney'][-155:] / df['SellTradeNum'][-155:].replace(0, np.nan)) * df['weight'][-155:]).sum(axis = 1)  
        bun_to_bn_w = ((df['BuyUniqueOrderNum'][-2:] / df['BuyTradeNum'][-2:].replace(0, np.nan)) * df['weight'][-2:]).sum(axis = 1)
        
        rs = rsi(sa_to_sn_w, 50)[-53:]
        pr = ts_pred(rs, 50)[-2:]
        factor = pr / bun_to_bn_w
        return np.nanmean(factor.values)