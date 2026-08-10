# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 09:16:03 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class HDLD_ae_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_hs300','turnover_hs300', 'weight_boolean_hs300', 'close_hs300', 'open_hs300']

        super(HDLD_ae_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):
        df_s = (data['amount_hs300'].rolling(120, min_periods = 15).sum())[data['weight_boolean_hs300']]
        ret_30 = (data['turnover_hs300']/data['turnover_hs300'].shift(30)-1)[data['weight_boolean_hs300']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0)
        mask = temp1*temp5
        temp1 = pd.DataFrame(np.where(data['open_hs300']>data['close_hs300'], data['open_hs300'], data['close_hs300']))
        temp2 = pd.DataFrame(np.where(data['open_hs300']>data['close_hs300'], data['close_hs300'], data['open_hs300']))
        temp1.index = data['open_hs300'].index
        temp2.index = data['open_hs300'].index
        temp1.columns = data['open_hs300'].columns
        temp2.columns = data['open_hs300'].columns
        t_pcorr = (temp1.diff()+temp2.diff())

        tempdf = (t_pcorr*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(60, min_periods = 30).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor