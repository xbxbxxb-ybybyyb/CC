from future_factor import FutureFactor
import numpy as np


class MinuteWilliamsR(FutureFactor):
    '''
    Description: -(TodayHigh - close) / (TodayHigh - TodayLow)
    Class: Return_Risk
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 0
    data_dict = {}
    data_dict['Continuous_Data'] = {'IC':['close', 'TodayHigh', 'TodayLow']}
    normalize_size = 60 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        f = -(data['TodayHigh_cont_IC'].values[-1] - data['close_cont_IC'].values[-1]) / (data['TodayHigh_cont_IC'].values[-1] - data['TodayLow_cont_IC'].values[-1])
        return f
