# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 10:26:32 2021

@author: appadmin
"""

from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class BS_7_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['buy_superorder_money_300', 'buy_bigorder_money_300', 'amount_300']

        super(BS_7_CC_IF, self).__init__(required_columns=required_columns
                                  )

    def on_bar(self, data):
        factor = (data['buy_superorder_money_300']+data['buy_bigorder_money_300'])/(data['amount_300'])
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        factor = factor.rolling(20, min_periods = 2).mean()

        factor = factor.mean(axis = 1)
        factor = ts_rank(factor.to_frame())
        factor.columns = [self.__class__.__name__]

        return factor