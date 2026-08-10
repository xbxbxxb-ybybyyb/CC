# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 16:25:02 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


class SLHS_CC_ICIF_IF(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot']

        super(SLHS_CC_ICIF_IF, self).__init__(
                                  required_columns=required_columns)
        
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    def rolling_linear_reg(self, x, y, window_size):
        x2=np.power(x,2)
        xy=x*y
        window = np.ones(int(window_size))
        a1=np.convolve(xy, window, 'full')*window_size
        a2=np.convolve(x, window, 'full')*np.convolve(y, window, 'full')
        b1=np.convolve(x2, window, 'full')*window_size
        b2=np.power(np.convolve(x, window, 'full'),2)
        alphas=(a1-a2)/(b1-b2)
        #betas=(np.convolve(y, window, 'full')-alphas*np.convolve(x, window, 'full'))/float(window_size)
        alphas=alphas[:-1*(window_size-1)] #numpy array of rolled alpha
        #betas=betas[:-1*(window_size-1)] 
        alphas[:window_size-1] = np.nan
        return alphas
    
    def on_bar(self, data):


        high_spot = data['high_spot'].values
        
        ind = list(range(len(high_spot)))

        m_vwap_ind_r = self.rolling_linear_reg(ind, high_spot, 60)
        #factor = pd.Series(data['close_spot_if'].rolling(25, min_periods = 1).skew()).to_frame()
        factor = pd.Series(m_vwap_ind_r).to_frame()
        factor.index = data['high_spot'].index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        #factor[factor>1] = np.nan
        factor[factor<=-0.5] = np.nan
        factor = self.ts_rank(factor, 242*6)
        factor = self.ts_rank(factor)
        factor[factor<=-0.5] = 0

        return factor