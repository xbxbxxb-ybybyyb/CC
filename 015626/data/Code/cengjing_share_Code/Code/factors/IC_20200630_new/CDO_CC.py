# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 09:18:46 2020

@author: appadmin
"""

import pandas as pd
import numpy as np

from factor_generator import FactorGenerator
from operators_cc import *

class CDO_CC(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'open', 'recent_month_mask']
        super(CDO_CC, self).__init__(required_columns=required_columns)
                                 

    
    def on_bar(self, data):

        cdo_r = data['close'].rolling(120, min_periods = 60).mean()/data['open'].rolling(120, min_periods = 60).mean()
        factor = (cdo_r[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, method = 'ts_rank')
        #factor = factor.rolling(3,min_periods=1).mean()
        factor[factor<=-0.5]=0
        return factor

