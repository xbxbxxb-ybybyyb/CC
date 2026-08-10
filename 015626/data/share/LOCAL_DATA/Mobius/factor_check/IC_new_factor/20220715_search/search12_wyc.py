from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_all_wsc import *

class search12_wyc(FutureFactor):
#     factor = ts_pred(bbands_down(dema(ba_to_bn_w, 2), 10), 20)
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeMoney','BuyTradeNum','weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    
    def calculate(self, df):        
        ba_to_bn_w = ((df['BuyTradeMoney'][-45:] / df['BuyTradeNum'][-45:]) * df['weight'][-45:]).sum(axis = 1)
        temp1 = dema(ba_to_bn_w, 2)[-41:]
        temp2 = bbands_down(temp1, 10)[-21:]
        factor = ts_pred(temp2, 20).values[-1]
        return factor