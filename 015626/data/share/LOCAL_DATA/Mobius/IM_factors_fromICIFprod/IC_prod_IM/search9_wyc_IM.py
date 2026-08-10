from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_all_wsc import *

class search9_wyc_IM(FutureFactor):
#     factor = add2(sun_to_sn, up_down_ratio(sun, 100, 10))
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    
    def calculate(self, df):        
        sun_to_sn = (df['SellUniqueOrderNum'][-1:].sum(axis = 1) / df['SellTradeNum'][-1:].replace(0, np.nan).sum(axis = 1)).values[-1]        
        sun = df['SellUniqueOrderNum'][-110:].sum(axis = 1)
        return up_down_ratio(sun, 100, 10).values[-1] + sun_to_sn