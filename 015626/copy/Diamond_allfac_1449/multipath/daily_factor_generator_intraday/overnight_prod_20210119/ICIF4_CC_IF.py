# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 13:14:43 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class ICIF4_CC_IF(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close_spot']

        super(ICIF4_CC_IF, self).__init__(*args, required_columns=required_columns, **kwargs)

    

    
    def on_bar(self, data):

        temp = data['close_spot'].rolling(60, min_periods = 15).mean() - data['close_spot'].shift(20).rolling(40, min_periods = 7).mean()
        factor = temp.to_frame()

        factor = np.abs(factor)

        factor = ts_rank(factor)

        factor[factor<=-0.5] = 0
        factor = factor.iloc[factor.index.indexer_at_time('14:49:00')]
        factor.index = pd.to_datetime(factor.index.date)
        factor.index.name = 'dt'
        factor.columns = [self.__class__.__name__]
        return factor