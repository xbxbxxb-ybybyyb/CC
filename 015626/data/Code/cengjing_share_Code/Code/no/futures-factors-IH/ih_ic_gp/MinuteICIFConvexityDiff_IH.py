import numpy as np
from future_factor import FutureFactor

class MinuteICIFConvexityDiff_IH(FutureFactor):
    '''
    Description: mean(pct_chg(pct_chg(close_000905.SH, 1), 1) - pct_chg(pct_chg(close_000300.SH, 1), 1), 90)
    Class: Multi-Variety
    Author: jinpx, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close'], '000016.SH':['close']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        IC_close = data['close_000905.SH'].values
        IF_close = data['close_000016.SH'].values
        
        IC_r = np.diff(IC_close) / IC_close[:-1]
        IF_r = np.diff(IF_close) / IF_close[:-1]
        
        IC_convexity = np.diff(IC_r) / IC_r[:-1]
        IF_convexity = np.diff(IF_r) / IF_r[:-1]
        
        N = 90        
        convexity_diff = IC_convexity[-N:] - IF_convexity[-N:]
        convexity_diff[np.isinf(convexity_diff)] = np.nan
        f = np.nanmean(convexity_diff)        
        
        return f