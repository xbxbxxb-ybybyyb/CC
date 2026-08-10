# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 10:25:26 2021

@author: appadmin
"""

from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class SHIBOR_Overnight_return_CC(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['SHIBOR']
        super(SHIBOR_Overnight_return_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=6, **kwargs)

    def on_bar(self, df):
        t = df['SHIBOR'].diff().to_frame()
        t.columns = [self.__class__.__name__]
        return t