# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 18:52:13 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *


class fvs2_ind_IFIC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if', 'close_if', 'recent_month_mask']

        super(fvs2_ind_IFIC_CC, self).__init__(
                                  required_columns=required_columns)
    

    def on_bar(self, data):

        close_spot = data['close_spot_if']
        close = data['close_if']
        vwtc_r = close.rolling(40, min_periods=15).corr(close_spot)
        vwtc_r  = vwtc_r.replace([-np.inf, np.inf], np.nan)
        vwtc_r = vwtc_r[data['recent_month_mask']]
        factor = (vwtc_r*(np.sign(-(close.sub(close_spot,axis=0))))[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor = np.abs(factor)
        factor.iloc[:, 0] = factor.iloc[:, 0].rolling(5, min_periods = 2).mean()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor

