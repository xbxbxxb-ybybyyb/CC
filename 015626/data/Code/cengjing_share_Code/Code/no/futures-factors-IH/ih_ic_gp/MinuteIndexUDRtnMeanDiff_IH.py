import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew


class  MinuteIndexUDRtnMeanDiff_IH(FutureFactor):
    '''
    Description: 
    Class: Price_CS_Stat
    Author: shentq  modeified by liuz
    '''
    data_type = 'IndexStock'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Stock'] = ['close', 'open']

    
    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        close = data['close'].values
        open_ = data['open'].values

        rtn = close/open_-1
        rtn[np.isinf(rtn)] = np.nan
        up_rtn = np.nanmean(np.where(rtn>0,rtn, np.nan),axis=1)

        down_rtn = np.nanmean(np.where(rtn<0,rtn, np.nan),axis=1)
        factor= np.nanmean(up_rtn[-20:])+ np.nanmean(down_rtn[-20:])
            
        return factor




