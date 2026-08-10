# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 10:24:47 2021

@author: appadmin
"""

from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class JPY_AUD_CC(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['AUDJPY']
        super(JPY_AUD_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=4, **kwargs)

    def on_bar(self, df):
        t = -df['AUDJPY'].diff().to_frame()
        t.columns = [self.__class__.__name__]
        return t