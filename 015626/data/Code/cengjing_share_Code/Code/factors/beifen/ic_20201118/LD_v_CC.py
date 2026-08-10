# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 18:14:01 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator import FactorGenerator
import numpy as np
from joblib import Parallel, delayed

class LD_v_CC(FactorGenerator):
    def __init__(self):
        required_columns=['recent_month_mask', 'volume']

        super(LD_v_CC, self).__init__(required_columns=required_columns
                                  )
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def to_ts(self, df, ret, weight, LS = True, Lag = False):
        ret = ret*weight
        #df = df.fillna(0)
        #print((df!=0).astype(int).sum(axis = 1))
        if LS == True:
            if Lag == False:
                return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)-(df.lt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)
            else:
                return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)-(df.lt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)
        else:
            if Lag == False:
                return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)
            else:
                return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)
    
    def decay_linear(self, x1, window):
        interval = x1.shape[1]
        num = np.array(list(range(window))) + 1.0
        coe = np.tile(num, (x1.shape[0],1))
        def _sub_decay_linear(k, coe):
            data = x1[:, k:window + k]
            isnan = np.isnan(data)
            coe[isnan] = np.nan
            sum_days = np.nansum(coe,axis = 1)
            sum_days = np.tile(sum_days,(window,1)).T
            coe = coe/sum_days
            decay = np.nansum(coe*data,axis = 1)
            decay[isnan[:,-1]] = np.nan
            return decay
        tmparray = np.array(Parallel(n_jobs=-1)(delayed(_sub_decay_linear)(k + 1, coe) for k in range (0, interval-window))).T
        result = np.full([x1.shape[0], window],np.nan)
        result = np.column_stack([result,tmparray])
        return result
    
    def on_bar(self, data):
        volume = ((data['volume'])[data['recent_month_mask']]).mean(axis = 1)

        v_max = np.array([volume.rolling(40, min_periods = 20).max()])

        prstd_r = pd.Series(self.decay_linear(v_max, 30)[0])
        prstd_r.index = volume.index

        
        factor = self.ts_rank(prstd_r.to_frame(), 3000)
        factor.columns = [self.__class__.__name__]
        return factor
