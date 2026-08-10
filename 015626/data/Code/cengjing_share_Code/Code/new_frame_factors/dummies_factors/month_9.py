# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:35:33 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class month_9(FutureFactor):

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
        if t.month == 9:
            factor = 1
        else:
            factor = 0
        return factor