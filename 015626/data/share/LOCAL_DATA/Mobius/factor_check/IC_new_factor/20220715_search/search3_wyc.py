from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_all_wsc import *

# factor = ts_pred(bun_to_bn_w, 30) * -1
class search3_wyc(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    
    def calculate(self, df):        
        bun_to_bn_w = ((df['BuyUniqueOrderNum'][-31:] / df['BuyTradeNum'][-31:].replace(0, np.nan)) * df['weight'][-31:]).sum(axis = 1)
        return ts_pred(bun_to_bn_w, 30).values[-1] * -1