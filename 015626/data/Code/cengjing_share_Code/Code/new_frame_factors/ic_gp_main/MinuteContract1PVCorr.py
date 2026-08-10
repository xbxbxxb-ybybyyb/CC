from future_factor import FutureFactor
import numpy as np


class MinuteContract1PVCorr(FutureFactor):
    '''
    Description: -corr(close_01, volume_01, 90)
    Class: All_Contract
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = {}
    data_dict['Other_Future_Instrument'] = {'01': ['close', 'volume']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close_01'].values[-90:]
        volume = data['volume_01'].values[-90:]
        f = -np.corrcoef(close, volume)[0, 1]
        return f
