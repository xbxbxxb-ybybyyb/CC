# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 13:15:32 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class LminLmean_ind_CC(FactorGenerator):
    def __init__(self):
        required_columns =['low_spot']
        super(LminLmean_ind_CC, self).__init__(
                                  required_columns=required_columns)
    

    def on_bar(self, data):

        ctl_r = -data['low_spot'].rolling(50, min_periods =30).min()/data['low_spot'].rolling(30, min_periods =15).mean()
        factor = ctl_r.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor