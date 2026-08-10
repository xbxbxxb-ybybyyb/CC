from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_all_wsc import *

class search10_wyc_IM(FutureFactor):
#     factor = bbands_down(ts_corr(sun, sa_y, 10), 10)
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['SellTradeMoney', 'SellUniqueOrderNum']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    
    def calculate(self, df):        
        sa_y = df['SellTradeMoney'][-20:].sum(axis = 1)        
        sun = df['SellUniqueOrderNum'][-20:].sum(axis = 1)
        tc = ts_corr(sun, sa_y, 10)[-10:]
        factor = bbands_down(tc, 10).values[-1]
        return factor