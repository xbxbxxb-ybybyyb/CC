# -*- coding: utf-8 -*-
"""
Created on Wed May 25 15:47:39 2022

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk

class NL_CC_2_IF(FutureFactor):

    data_type = 'Future'
    days_past = 4
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        hclose = data['close_000300.SH'].iloc[-862:]
        roll_max = ts_max(hclose, 30)
        drawdown = hclose-roll_max

        max_drawdown = ts_min(drawdown, 30)

        temp = ((hclose- hclose.shift(30))/max_drawdown)#[data['weight_boolean_zz500']]

        temp2 = (temp)       

        factor = ts_rank(temp2, 800).values[-1]

        #factor = -ts_rank(1 - abs(factor))
    
        return -(1-abs(factor))
