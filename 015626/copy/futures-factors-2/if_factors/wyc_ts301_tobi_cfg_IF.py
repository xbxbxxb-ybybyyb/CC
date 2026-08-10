# -*- coding: utf-8 -*-
import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class wyc_ts301_tobi_cfg_IF(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyOrderAmt_total', 'SellOrderAmt_total', 'amount']
    normalize_size = 600
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy = data['BuyOrderAmt_total'].iloc[-1].values
        sell = data['SellOrderAmt_total'].iloc[-1].values
        amt = data['amount'].iloc[-15:].sum().values
        buy = ma.array(buy, mask=(amt >= np.quantile(amt, 0.9)))
        sell = ma.array(sell, mask=(amt >= np.quantile(amt, 0.9)))
        
        buy = np.nansum(list(buy))
        sell = np.nansum(list(sell))
        
        factor =  (buy - sell) / (buy + sell)
        return factor