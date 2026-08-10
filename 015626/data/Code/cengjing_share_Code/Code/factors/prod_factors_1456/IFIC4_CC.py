# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 13:17:31 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class IFIC4_CC(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot_if']
        super(IFIC4_CC, self).__init__(required_columns=required_columns)
    

    def on_bar(self, data):

        temp = data['close_spot_if'].rolling(60, min_periods = 15).mean() - data['close_spot_if'].shift(20).rolling(40, min_periods = 7).mean()
        factor = temp.to_frame()

        factor = np.abs(factor)
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor