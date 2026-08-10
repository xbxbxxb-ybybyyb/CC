import numpy as np
from future_factor import FutureFactor

class MinuteTodayHMLoverOpen(FutureFactor):
    '''
    Description: mean((TodayHigh - TodayLow) / TodayOpen, 25)
    Class: Price_Stat
    Author: jinpx, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['TodayHigh', 'TodayLow', 'TodayOpen']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        N = 25
        todayhigh = data['TodayHigh_cont_IC'].values[-N:]
        todaylow = data['TodayLow_cont_IC'].values[-N:]
        todayopen = data['TodayOpen_cont_IC'].values[-N:]
        
        f = np.nanmean((todayhigh-todaylow)/todayopen)
        
        return f