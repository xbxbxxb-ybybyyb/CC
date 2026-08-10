import numpy as np
from future_factor import FutureFactor

class MinuteLocalLowHighNumDiff(FutureFactor):
    '''
    Description: count(local_low) - count(local_high)
    Class: Local_High_Low
    Author: hefj, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        index_close = data['close_000905.SH'].values
        
        N = 237   
        w = np.arange(1, N - 1)
        w = w / np.nansum(w)
        
        index_r = np.diff(index_close[-N:]) / index_close[-N:][:-1]
        index_r_std = np.nanstd(index_r)
        local_low = np.nansum(w[(index_r[:-1] < -index_r_std) & (index_r[1:] > index_r_std)])
        local_high = np.nansum(w[(index_r[:-1] > index_r_std) & (index_r[1:] < -index_r_std)])
        
        f = local_low - local_high       
        if np.isnan(f) or np.isinf(f):
            f = 0
        
        return f