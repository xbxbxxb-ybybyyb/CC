import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew



class  MinuteIndexHighBetaRtn(FutureFactor):
    '''
    Description: 
    Class: Group_Stat
    Author: shentq  modeified by liuz
    '''
    data_type = 'IndexStock'
    instrument_type='recent'
    days_past=2
    data_dict=dict()
    data_dict['Stock'] = ['close', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        index_close = data['close_000905.SH'].values
        close = data['close'].values
        adjfactor = data['adjfactor'].values

        close_adj = close*adjfactor
        rtn = close_adj[1:]/close_adj[:-1]-1

        index_rtn = index_close[1:] / index_close[:-1] - 1

        rtn[np.isinf(rtn)] = np.nan
        index_rtn[np.isinf(index_rtn)] = np.nan

        adj_rtn_237 = rtn[-237:]
        index_rtn_237 = index_rtn[-237:]
        adj_rtn_30 = rtn[-30:] 
        cov_matrix = np.cov(adj_rtn_237.T,index_rtn_237.reshape(237,-1).T)
        cov_rtn = cov_matrix[-1][:-1]
        index_rtn_std = np.nanstd(index_rtn_237)

        beta = cov_rtn / np.power(index_rtn_std,2)
        factor = np.nanmean(np.nanmean(adj_rtn_30[:,beta > 3],axis=0))

        if np.isnan(factor):
            factor = 0
            
            
        return factor

