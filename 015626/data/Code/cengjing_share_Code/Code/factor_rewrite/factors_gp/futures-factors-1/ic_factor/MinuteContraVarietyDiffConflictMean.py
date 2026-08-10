import numpy as np
import pandas as pd
from future_factor import FutureFactor

    

class  MinuteContraVarietyDiffConflictMean(FutureFactor):
    '''
    Description: "mean(where(((Index_ClosePx / Index_OpenPx - 1 > 0) & (Index_Other2_ClosePx / Index_Other2_OpenPx - 1 < 0)) |
            ((Index_ClosePx / Index_OpenPx - 1 < 0) & (Index_Other2_ClosePx / Index_Other2_OpenPx - 1> 0)), Index_ClosePx / Index_OpenPx - Index_Other2_ClosePx / Index_Other2_OpenPx, nan), 20)"
    Class:Multi-Variety
    Author:  shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='main'
    days_past=1
    data_dict=dict()
    data_dict['Index_Id'] ={'000905.SH':['close','open'],'000016.SH':['close','open']}
    
    normalize_size=1*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        index_close =  data['close_000905.SH'].values 
        index_other_close =  data['close_000016.SH'].values 
        index_open =  data['open_000905.SH'].values 
        index_other_open =  data['open_000016.SH'].values 

        index_rtn_list =index_close/index_open-1
        other_rtn_list = index_other_close/index_other_open-1

        conflict_rtn_list = []

        for i in range(20):
            idx = i-20
            if (index_rtn_list[idx] > 0 and other_rtn_list[idx] < 0) or (index_rtn_list[idx] < 0 and other_rtn_list[idx] > 0):
                conflict_rtn_list.append(index_rtn_list[idx] - other_rtn_list[idx])

        if len(conflict_rtn_list) == 0:
            factor = 0
        else:
            factor =np.nanmean(conflict_rtn_list)

        return factor