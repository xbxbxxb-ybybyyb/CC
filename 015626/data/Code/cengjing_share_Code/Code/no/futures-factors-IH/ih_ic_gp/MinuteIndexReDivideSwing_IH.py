import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIndexReDivideSwing_IH(FutureFactor):
    '''
    Description: pct_chg(index_close, 60) / ((max(index_high, 60) - min(index_low, 60)) / delay(index_close, 60))
    Class: Return_Risk
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 20
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close', 'high', 'low']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        index_close = data['close_000016.SH'].values
        index_high = data['high_000016.SH'].values
        index_low = data['low_000016.SH'].values
        
        N = 60
        index_close_past = index_close[:self.days_past*240]
        index_high_past = index_high[:self.days_past*240]
        index_low_past = index_low[:self.days_past*240]
        index_r_past = (index_close_past[N:] - index_close_past[:-N]) / index_close_past[:-N]
        index_swing_past = (bn.move_max(index_high_past, N) - bn.move_min(index_low_past, N))[N:] / index_close_past[:-N]
        f_past = index_r_past / index_swing_past
        f_past_mean = np.nanmean(f_past)
        f_past_std = np.nanstd(f_past)
        
        index_r = (index_close[-1] - index_close[-N-1]) / index_close[-N-1]
        index_swing = (np.max(index_high[-N:]) - np.min(index_low[-N:])) / index_close[-N-1]
        f_original = index_r / index_swing
        
        f = (f_original - f_past_mean) / f_past_std
        if f > 3:
            f = 3
        elif f < -3:
            f = -3
        
        return f