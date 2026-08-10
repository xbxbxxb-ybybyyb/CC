from future_factor import FutureFactor
import numpy as np


class MinuteWilliamsR_IF_IH(FutureFactor):
    '''
    Description: -(TodayHigh - close) / (TodayHigh - TodayLow)
    Class: Return_Risk
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 0
    data_dict = {}
    data_dict['Continuous_Data'] = {'IH':['close', 'TodayHigh', 'TodayLow']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        f = -(data['TodayHigh_cont_IH'].values[-1] - data['close_cont_IH'].values[-1]) / (data['TodayHigh_cont_IH'].values[-1] - data['TodayLow_cont_IH'].values[-1])
        return f
