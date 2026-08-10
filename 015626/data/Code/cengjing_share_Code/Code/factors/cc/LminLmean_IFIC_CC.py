# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:33:38 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class LminLmean_IFIC_CC(FactorGenerator):
    def __init__(self):
        required_columns =['low_if', 'recent_month_mask']
        super(LminLmean_IFIC_CC, self).__init__(
                                  required_columns=required_columns)
    

    def on_bar(self, data):

        ctl_r = -data['low_if'].rolling(60, min_periods =15).min()/data['low_if'].rolling(30, min_periods =10).mean()
        factor = (ctl_r[data['recent_month_mask']]).mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 242*3)
        return factor