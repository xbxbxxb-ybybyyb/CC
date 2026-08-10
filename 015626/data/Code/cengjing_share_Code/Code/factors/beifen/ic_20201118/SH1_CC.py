# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 09:48:28 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *


class SH1_CC(FactorGenerator):
    def __init__(self):
        required_columns=['recent_month_mask', 'share']

        super(SH1_CC, self).__init__(required_columns=required_columns
                                  )
    
    def on_bar(self, data):
        volume = ((data['share'])[data['recent_month_mask']]).mean(axis = 1)

        share_std = volume.rolling(70, min_periods = 35).std()
        factor = ts_rank(share_std.to_frame(), 242)
        factor.columns = [self.__class__.__name__]
        return factor