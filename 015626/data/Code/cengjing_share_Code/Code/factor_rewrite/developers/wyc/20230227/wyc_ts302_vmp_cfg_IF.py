# -*- coding: utf-8 -*-
import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class wyc_ts302_vmp_cfg_IF(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['vwap_midprice']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        factor = data['vwap_midprice'].iloc[-3:].values
        factor = np.nanmean(factor) * -1
        return factor