# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 15:31:03 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class HHLS_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'high_zz500', 'weight_boolean_zz500']

        super(HHLS_CFG_CC, self).__init__(required_columns=required_columns
                                  )
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
            
    def on_bar(self, data): 
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        hdl_r = data['high_zz500'].rolling(40, min_periods = 15).max() - data['high_zz500'].shift(40).rolling(40, min_periods = 7).max()
        factor = hdl_r.rolling(10, min_periods = 2).mean()
        factor = (factor[bool_df]).mean(axis = 1)  
        factors = self.ts_rank(factor.to_frame())
        factors.columns = [self.__class__.__name__]
        #factors[factors<=-0.5] = np.nan
        return factors
