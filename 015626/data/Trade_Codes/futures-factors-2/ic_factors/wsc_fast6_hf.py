# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 17:52:08 2022

@author: appadmin
"""
import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
from operators_wsc_1_0 import *


class wsc_fast6_hf(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum', 'amount']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    handle_preadj = False
    
    def calculate(self, data):
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-3:]
        BuyTradeNum = data['BuyTradeNum'].values[-3:]
        
        df_s = data['amount'].values[-3:]
        
        amount_mask = np.nanquantile(df_s, 0.9, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        factor_raw = BuyTradeNum
        factor_raw_after_mask = ma.array(factor_raw, mask=(df_s<=amount_mask))
        factor_raw_after_mask = np.nansum(factor_raw_after_mask, axis=1)
        
        factor_raw2 =  BuyUniqueOrderNum
        factor_raw_after_mask2 = ma.array(factor_raw2, mask=(df_s<=amount_mask))
        factor_raw_after_mask2 = np.nansum(factor_raw_after_mask2, axis=1)
        
        factor_mean = factor_raw_after_mask / r(factor_raw_after_mask2)

        return np.nanmean(factor_mean)