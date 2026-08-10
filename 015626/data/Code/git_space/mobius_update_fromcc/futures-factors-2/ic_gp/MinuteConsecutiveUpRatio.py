import numpy as np
import pandas as pd
from future_factor import FutureFactor


    


class  MinuteConsecutiveUpRatio(FutureFactor):
    '''
    Description: "sum(where((delay(Index_ClosePx, 2) < delay(Index_ClosePx, 1)) & (Index_ClosePx < delay(Index_ClosePx, 1)), 1, 0), 120)
                    / sum(where(delay(Index_ClosePx, 1) < Index_ClosePx, 1, 0), 120)"
    Class: MTM
    Author: hefj  modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Index_Id'] ={'000905.SH':['close']}
    
    normalize_size=1*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close_000905.SH'].values
        close_temp =  close[-120:]
        up = (close[1:] > close[:-1]).sum()
        consecutive_up = ((close_temp[:-2] < close_temp[1: -1]) & (close_temp[2:] > close_temp[1: -1])).sum()
        return consecutive_up/up
    
    


    