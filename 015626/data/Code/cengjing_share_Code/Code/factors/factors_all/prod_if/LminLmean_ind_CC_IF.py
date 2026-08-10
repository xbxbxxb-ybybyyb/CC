# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 14:31:16 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator import FactorGenerator

class LminLmean_ind_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns =['low_spot_if']
        super(LminLmean_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)
    


    def on_bar(self, data):

        ctl_r = -data['low_spot_if'].rolling(45, min_periods =30).min()/data['low_spot_if'].rolling(25, min_periods =15).mean()
        factor = ctl_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor
