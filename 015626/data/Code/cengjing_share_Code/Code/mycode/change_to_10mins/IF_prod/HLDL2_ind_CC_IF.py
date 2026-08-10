# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 17:44:46 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np
from factor_generator import FactorGenerator

# demo
class HLDL2_ind_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot_if', 'low_spot_if']

        super(HLDL2_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)



    def on_bar(self, data):


        t_pcorr = (data['high_spot_if'].diff()+data['low_spot_if'].diff()).rolling(90, min_periods = 45).mean()
        factor = t_pcorr.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor)
        factor[factor<0] = 0
        return factor
