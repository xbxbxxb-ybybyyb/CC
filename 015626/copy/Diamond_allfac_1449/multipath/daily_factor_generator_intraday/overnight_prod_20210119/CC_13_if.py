# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 17:48:16 2020

@author: appadmin
"""

from operators_cc import *
import pandas as pd
from factor_generator import FactorGenerator

class CC_13_if(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=[ 'close_spot_if']

        super().__init__(*args, required_columns=required_columns, **kwargs)

            
    def on_bar(self, data):
        temp = data['close_spot_if'].rolling(90, min_periods = 2).mean().diff()
        dd1 = temp.between_time('13:00', '14:49')
        dd1 = dd1.groupby(dd1.index.date).mean()
        dd1 = ts_rank(dd1.to_frame(), 70)
        dd1.index = pd.to_datetime(dd1.index)
        dd1.index.name = 'dt'
        dd1.columns = [self.__class__.__name__]
        return dd1