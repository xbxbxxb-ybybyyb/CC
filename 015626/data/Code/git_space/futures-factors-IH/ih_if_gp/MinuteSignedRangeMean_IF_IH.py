from future_factor import FutureFactor
import numpy as np


class  MinuteSignedRangeMean_IF_IH(FutureFactor):
    '''
    Description: mean(where(ClosePx > OpenPx, HighPx / LowPx, -HighPx / LowPx), 120)
    Class:MTM
    Author:  shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()

    data_dict['Index_Id'] = {'000016.SH': ['high', 'low','open', 'close']}
    normalize_size= 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        open_ = data['open_000016.SH'].values 
        close = data['close_000016.SH'].values 
        high = data['high_000016.SH'].values 
        low = data['low_000016.SH'].values 
        
        range_ =high/low
        sign = np.sign(close-open_)
        
        signed_range = (sign*range_)
        factor = np.nanmean(signed_range[-15:])
        return  factor
