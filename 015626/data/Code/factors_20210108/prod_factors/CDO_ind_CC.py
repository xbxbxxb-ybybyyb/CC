# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 12:20:34 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *


class CDO_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['open_spot', 'close_spot']

        super(CDO_ind_CC, self).__init__(
                                  required_columns=required_columns)

    
    def on_bar(self, data):

        odc_ind_r = data['close_spot'].rolling(150, min_periods = 60).mean()-data['open_spot'].rolling(150, min_periods = 60).mean()
        factor = odc_ind_r.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, method = 'ts_rank')
        factor[factor<=-0.5] = 0
        return factor
