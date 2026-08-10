from future_factor import FutureFactor
import numpy as np


class MinuteTwapCloseRatio(FutureFactor):
    '''
    Description: -mean(twap, 30) / mean(close, 30)
    Class: MTM
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Future_Data'] = ['close', 'twap']
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close'].values[-30:]
        twap = data['twap'].values[-30:]
        f = -np.mean(twap) / np.mean(close)
        return f
