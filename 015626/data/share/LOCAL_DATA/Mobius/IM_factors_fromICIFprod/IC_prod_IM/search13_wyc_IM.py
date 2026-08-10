from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_all_wsc import *

class search13_wyc_IM(FutureFactor):
#     factor = midpoint(neg1(bun_r), 10)
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum','SellUniqueOrderNum']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    
    def calculate(self, df):        
        bun_r = -1 * df['BuyUniqueOrderNum'][-10:].sum(axis = 1) / (df['BuyUniqueOrderNum'][-10:] + df['SellUniqueOrderNum'][-10:]).sum(axis = 1).replace(0, np.nan)
        return (np.nanmax(bun_r) + np.nanmin(bun_r)) / 2