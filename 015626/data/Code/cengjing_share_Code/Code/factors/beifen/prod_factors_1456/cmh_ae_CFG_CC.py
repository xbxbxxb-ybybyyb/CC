# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 17:26:31 2021

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class cmh_ae_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_zz500','amount_zz500', 'turnover_zz500', 'high_zz500', 'close_zz500']

        super(cmh_ae_CFG_CC, self).__init__(required_columns=required_columns
                                  )
        
    def on_bar(self, data):
        df_s = (data['amount_zz500'].rolling(120, min_periods = 15).sum())[data['weight_boolean_zz500']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)
        ret_30 = (data['turnover_zz500']/data['turnover_zz500'].shift(30)-1)[data['weight_boolean_zz500']]
        ret_30 = ret_30.replace([-np.inf, np.inf], np.nan)
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0)

        bool_df = temp1&temp5

        vwtc_r = data['high_zz500']-(data['close_zz500'].rolling(120, min_periods = 30).mean())
        vwtc_r = rolling_norm(vwtc_r)
        factor = (vwtc_r*bool_df).mean(axis = 1).to_frame().rolling(10, min_periods = 5).mean()
        factor = ts_rank(factor, 242)
        factor.columns = [self.__class__.__name__]
        return factor