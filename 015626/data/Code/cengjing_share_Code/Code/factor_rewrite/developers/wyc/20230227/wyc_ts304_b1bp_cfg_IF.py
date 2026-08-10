# -*- coding: utf-8 -*-
import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class wyc_ts304_b1bp_cfg_IF(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['B1minus_BWeightedPx_5_to_midprice', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy = data['B1minus_BWeightedPx_5_to_midprice'].iloc[-1].values
        weight = data['weight'].iloc[-1].values
        buy = ma.array(buy, mask=(weight <= np.quantile(weight, 0.9)))
        
        buy = np.nanmean(list(buy))
        
        factor = buy * -1
        return factor