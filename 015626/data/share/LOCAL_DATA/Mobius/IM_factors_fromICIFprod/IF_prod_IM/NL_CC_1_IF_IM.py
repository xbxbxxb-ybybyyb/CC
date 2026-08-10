# -*- coding: utf-8 -*-
"""
Created on Wed May 25 15:35:11 2022

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk

class NL_CC_1_IF_IM(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 3
    data_dict = dict()
    data_dict['Stock'] = [ 'close']
    normalize_size = 1200
    normalize_type = 'ts_rank' 

    handle_preadj = False
    
    def calculate(self, data):
                
        hclose = data['close'].iloc[-472:]
        roll_max = ts_max(hclose, 35)
        drawdown = hclose-roll_max

        max_drawdown = ts_min(drawdown, 35)

        temp = ((hclose- hclose.shift(35))/max_drawdown)#[data['weight_boolean_zz500']]

        temp2 = (temp).mean(axis = 1)       

        factor = ts_rank(temp2, 400).iloc[-1]

        #factor = -ts_rank(1 - abs(factor))
    
        return -(1-abs(factor))
