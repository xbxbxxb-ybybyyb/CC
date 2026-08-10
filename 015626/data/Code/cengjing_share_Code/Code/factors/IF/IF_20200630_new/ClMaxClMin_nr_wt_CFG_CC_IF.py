# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 13:48:16 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class ClMaxClMin_nr_wt_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_hs300','weight_boolean_hs300', 'close_hs300', 'turnover_hs300']

        super(ClMaxClMin_nr_wt_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, df):
        stk_weight = (df['weight_hs300'])[df['weight_boolean_hs300']]
        turnover = (df['turnover_hs300'].rolling(60, min_periods = 15).mean())[df['weight_boolean_hs300']]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        
        mask = stk_weight*temp4
        m_vwap_ind_r = (df['close_hs300']).rolling(45, min_periods = 30).max()/df['close_hs300'].rolling(45, min_periods = 30).min()
        m_vwap_ind_r[np.abs(m_vwap_ind_r)>10000] = np.nan
        temp = rolling_norm(m_vwap_ind_r, 242*5)
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(5, min_periods = 2).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor