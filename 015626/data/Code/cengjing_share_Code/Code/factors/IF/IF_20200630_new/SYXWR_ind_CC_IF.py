# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 15:38:45 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator

class SYXWR_ind_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if', 'low_spot_if', 'open_spot_if', 'high_spot_if']

        super(SYXWR_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)

    


    def on_bar(self, data):

        temp1 = pd.Series(np.where(data['open_spot_if']>data['close_spot_if'], data['open_spot_if'], data['close_spot_if']))
        temp2 = pd.Series(np.where(data['open_spot_if']>data['close_spot_if'], data['close_spot_if'], data['open_spot_if']))
        temp1.index = data['open_spot_if'].index
        temp2.index = data['open_spot_if'].index
        a = (data['high_spot_if'] - temp1).rolling(35, min_periods = 15).mean()
        b = (data['high_spot_if'].rolling(35, min_periods = 15).max()-data['low_spot_if'].rolling(35, min_periods = 15).min())
        a[abs(a) < 1e-8] = np.nan
        b[abs(b) < 1e-8] = np.nan
        t_pcor = (data['high_spot_if']-temp1)/a
        t_pcor2 = (data['close_spot_if']-data['low_spot_if'].rolling(35, min_periods = 15).min())/b
        t_pcorr = (t_pcor2 - t_pcor).rolling(60, min_periods = 20).mean()
        factor = t_pcorr.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor
