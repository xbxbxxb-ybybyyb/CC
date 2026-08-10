import numpy as np
from future_factor import FutureFactor

class MinuteUpDownRangeSumRatio(FutureFactor):
    '''
    Description: (sum(where(close_000905.SH > open_000905.SH, high_000905.SH - low_000905.SH, 0), 30) 
                 - sum(where(close_000905.SH < open_000905.SH, high_000905.SH - low_000905.SH, 0), 30))
                / (sum(where(close_000905.SH > open_000905.SH, high_000905.SH - low_000905.SH, 0), 30) 
                 + sum(where(close_000905.SH < open_000905.SH, high_000905.SH - low_000905.SH, 0), 30))
    Class: MTM
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close','open','high','low']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 30
        close = data['close_000905.SH'].values
        close[close == 0] = np.nan
        op = data['open_000905.SH'].values
        op[op == 0] = np.nan
        high = data['high_000905.SH'].values
        high[high == 0] = np.nan
        low = data['low_000905.SH'].values
        low[low == 0] = np.nan
        
        range_temp = high[-lb:] - low[-lb:]
        up_temp = range_temp[close[-lb:] > op[-lb:]].sum()
        down_temp = range_temp[close[-lb:] < op[-lb:]].sum()
        
        return (up_temp - down_temp) / (up_temp + down_temp)