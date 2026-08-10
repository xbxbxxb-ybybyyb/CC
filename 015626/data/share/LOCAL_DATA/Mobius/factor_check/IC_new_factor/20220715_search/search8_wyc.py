from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_all_wsc import *

class search8_wyc(FutureFactor):
#     factor = div2(rsi(bun_to_bn_w, 80), bun_to_bn_w)
#     factor = ts_mean(factor, 5)
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    
    def calculate(self, df):        
        bun_to_bn_w = ((df['BuyUniqueOrderNum'][-170:] / df['BuyTradeNum'][-170:].replace(0, np.nan)) * df['weight'][-170:]).sum(axis = 1)
        temp = rsi(bun_to_bn_w, 80)[-5:] / bun_to_bn_w[-5:]
        return np.nanmean(temp.values)