import numpy as np
import pandas as pd
from future_factor import FutureFactor
from scipy.stats import skew





class  MinuteSignedRangeMean(FutureFactor):
    '''
    Description: mean(where(ClosePx > OpenPx, HighPx / LowPx, -HighPx / LowPx), 120)
    Class:MTM
    Author:  shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='main'
    days_past=1
    data_dict=dict()
    data_dict['Future_Data'] = ['high', 'low','open', 'close']

    normalize_size=20*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        open_ = data['open'].values 
        close = data['close'].values 
        high = data['high'].values 
        low = data['low'].values 
        
        range_ =high/low
        sign = np.sign(close-open_)
        
        signed_range = (sign*range_)
        factor = np.nanmean(signed_range[-120:])
        return  factor