import numpy as np
from future_factor import FutureFactor

class MinuteICIFConvexityDiff_Refined(FutureFactor):
    '''
    Description: mean(pct_chg(pct_chg(close_000905.SH, 1), 1) - pct_chg(pct_chg(close_000300.SH, 1), 1), 90)
    Class: Multi-Variety
    Author: jinpx, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close'], '000300.SH':['close']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        IC_close = data['close_000905.SH'].values
        IF_close = data['close_000300.SH'].values

        N = 30
        IC_r = IC_close[N:] / IC_close[:-N] - 1
        IF_r = IF_close[N:] / IF_close[:-N] - 1
        
        IC_convexity = np.diff(IC_r)
        IF_convexity = np.diff(IF_r)
        
        N = 120
        convexity_diff = IC_convexity[-N:] - IF_convexity[-N:]
        f = np.nanmean(convexity_diff)        
        
        return f