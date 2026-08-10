from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_all_wsc import *

class search7_wyc(FutureFactor):
#     factor = sub2(up_down_ratio(fv, 120, 40), bun_to_bn)
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continous_Data'] = {'IC':['volume']}
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    
    def calculate(self, df):        
        bun_to_bn = (df['BuyUniqueOrderNum'][-1:].sum(axis = 1) / df['BuyTradeNum'][-1:].sum(axis = 1).replace(0, np.nan)).values[-1]
        fv = up_down_ratio(df['volume_cont_IC'][-160:], 120, 40).values[-1]
        return fv - bun_to_bn