# -*- coding: utf-8 -*-
import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class wyc_ts303_tbsuoc_cfg_IF(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['tran_buy_unique_order_count', 'tran_sell_unique_order_count']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy = np.nansum(data['tran_buy_unique_order_count'].iloc[-1].values)
        sell = np.nansum(data['tran_sell_unique_order_count'].iloc[-1].values)
        factor =  sell - buy
        return factor