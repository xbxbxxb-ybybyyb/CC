# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 13:41:12 2022

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class hour_10(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.hour == 10:
            return 1
        else:
            return 0
