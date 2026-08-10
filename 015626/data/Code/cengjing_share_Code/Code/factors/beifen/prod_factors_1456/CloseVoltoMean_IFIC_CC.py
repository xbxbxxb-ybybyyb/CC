# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 15:55:47 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class CloseVoltoMean_IFIC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if', 'recent_month_mask']

        super(CloseVoltoMean_IFIC_CC, self).__init__(
                                  required_columns=required_columns)


    def on_bar(self, data):

        prstd3_r = data['close_spot_if'].rolling(30, min_periods =10).std()/data['close_spot_if'].rolling(30, min_periods =15).mean()
        prstd3_r = prstd3_r.rolling(10, min_periods = 2).mean()
        factor = prstd3_r.to_frame()

        factor.columns =  [self.__class__.__name__]
        factor = rolling_norm(factor, method = 'ts_rank')

        return factor