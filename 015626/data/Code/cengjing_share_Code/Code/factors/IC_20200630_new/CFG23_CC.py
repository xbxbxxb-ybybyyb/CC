# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:53:33 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *



class CFG23_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'close_zz500', 'close_spot', 'weight_boolean_zz500']

        super(CFG23_CC, self).__init__(required_columns=required_columns
                                  )
    

    def on_bar(self, data):
        index_close = data['close_spot']
        stk_close = data['close_zz500']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        bool_df = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        x = np.array(range(len(data['close_zz500'])))
        holder = {}
        for item in data['close_zz500'].columns:
            close_spot = data['close_zz500'][item].values
            holder[item] = pd.Series(rolling_linear_reg(x, close_spot, 60))
        temp1 = pd.DataFrame(holder)
        temp1.index = data['close_zz500'].index
        temp1.columns = data['close_zz500'].columns
        temp = (temp1[bool_df]).mean(axis = 1)
        factor = rolling_norm(temp.to_frame())
        factor.columns = [self.__class__.__name__]
        factor[factor<=0] = 0
        factor[factor>1] = np.nan
        return factor