# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 16:24:40 2023

@author: appadmin
"""

from operators_wsc_1_0 import *
import numpy.ma as ma
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *

class srch_12(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [ 'SellTradeMoney', 'SellUniqueOrderNum', 'buy_smallorder_money', 'sell_smallorder_money_v2','weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        
        SellTradeMoney = data['SellTradeMoney'].values[-51:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-51:]
        weight = data['weight'].values[-51:]

        sa_to_sun_w = np.nansum(SellTradeMoney / replace_zero(SellUniqueOrderNum) * weight, axis = 1)
        
        buy_smallorder_money = data['buy_smallorder_money'].values[-131:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-131:]

        bba_4_r = np.nansum(buy_smallorder_money, axis = 1) / np.nansum(buy_smallorder_money + sell_smallorder_money_v2, axis = 1)
        
        factor = sub2(ts_argmin(sa_to_sun_w, 50)[-1], ts_maxmin_distance(rolling_norm(bba_4_r, 30), 100)[-1])
        
        return factor

