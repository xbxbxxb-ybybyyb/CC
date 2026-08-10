from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_all_wsc import *

class search6_wyc(FutureFactor):
#     factor = sub2(ts_mean(bun_to_bn, 100), bun_to_bn)
#     factor = ts_mean(factor, 3)
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    
    def calculate(self, df):        
        bun_to_bn = df['BuyUniqueOrderNum'][-103:].sum(axis = 1) / df['BuyTradeNum'][-103:].sum(axis = 1)
        factor = (ts_mean(bun_to_bn, 100) - bun_to_bn)[-3:].values
        return np.nanmean(factor)