import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew




class  MinuteUpDownNumDiff(FutureFactor):
    '''
    Description: sum(where(ClosePx > OpenPx, 1, 0), 30) - sum(where(ClosePx < OpenPx, 1, 0), 30)
    Class: MTM
    Author:  shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Future_Data'] = ['close', 'open']

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        close = data['close'].values 
        open_ = data['open'].values 

        rtn = close/open_-1
        
        up_rtn_list = []
        down_rtn_list = []
        
        for r in rtn:
            if r > 0:
                down_rtn_list.append(0)
                up_rtn_list.append(r)
            else:
                down_rtn_list.append(r)
                up_rtn_list.append(0)
                
        factor = np.nansum(np.array(up_rtn_list[-30:]) > 0) - np.nansum(np.array(down_rtn_list[-30:]) < 0)
        
        return  factor