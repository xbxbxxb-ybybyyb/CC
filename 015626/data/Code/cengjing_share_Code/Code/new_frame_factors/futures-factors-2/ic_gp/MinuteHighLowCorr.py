from future_factor import FutureFactor
import numpy as np


class MinuteHighLowCorr(FutureFactor):
    '''
    Description: corr(high, low, 90)
    Class: Price_Stat
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Future_Data'] = ['high', 'low']
    normalize_size = 3 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        high = data['high'].values[-90:]
        low = data['low'].values[-90:]
        f = np.corrcoef(high, low)[0, 1]
        return f
