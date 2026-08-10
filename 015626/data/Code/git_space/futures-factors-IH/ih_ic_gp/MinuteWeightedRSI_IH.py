import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew



class  MinuteWeightedRSI_IH(FutureFactor):
    '''
    Description: "sum(where(Index_ClosePx > Index_OpenPx, abs(Index_ClosePx / Index_OpenPx - 1), 0)[-120:] * (2.01 + cum_sum(where(Index_ClosePx > Index_OpenPx, -0.01, 0)[-120:])), 120)
/ (sum(where(Index_ClosePx > Index_OpenPx, abs(Index_ClosePx / Index_OpenPx - 1), 0)[-120:] * (2.01 + cum_sum(where(Index_ClosePx > Index_OpenPx, -0.01, 0)[-120:])), 120)
+ sum(where(Index_ClosePx < Index_OpenPx, abs(Index_ClosePx / Index_OpenPx - 1), 0)[-120:] * (2.01 + cum_sum(where(Index_ClosePx < Index_OpenPx, -0.01, 0)[-120:])), 120))"
    Class: MTM
    Author: shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Index_Id'] = {'000016.SH':['close','open']}

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        close = data['close_000016.SH'].values 
        open_ = data['open_000016.SH'].values 
        rtn_list = close/open_-1


        rtn_up_sum = 0
        rtn_down_sum = 0
        up_weight = 2
        down_weight = 2

        for i in range(120):
            if rtn_list[i-120] > 0:
                rtn_up_sum += abs(rtn_list[i-120]) * up_weight
                up_weight += -0.01
            elif rtn_list[i-120] < 0:
                rtn_down_sum += abs(rtn_list[i-120]) * down_weight
                down_weight += -0.01

        factor = rtn_up_sum / (rtn_up_sum+rtn_down_sum)

        return  factor
    
