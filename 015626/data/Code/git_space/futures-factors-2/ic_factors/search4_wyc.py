from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_all_wsc import *

class search4_wyc(FutureFactor):
    #div2(ts_pred(sa_to_sn_w, 60), bun_to_bn_w)
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum','weight','SellTradeNum','SellTradeMoney']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    
    def calculate(self, df):        
        sa_to_sn_w = ((df['SellTradeMoney'][-61:] / df['SellTradeNum'][-61:].replace(0, np.nan)) * df['weight'][-61:]).sum(axis = 1)        
        p = ts_pred(sa_to_sn_w, 60).values[-1]
        bun_to_bn_w = ((df['BuyUniqueOrderNum'][-1:] / df['BuyTradeNum'][-1:].replace(0, np.nan)) * df['weight'][-1:]).sum(axis = 1).values[-1]
        if bun_to_bn_w == 0:
            return np.nan
        else:
            return p / bun_to_bn_w