from future_factor import FutureFactor
import numpy as np


class MinuteContract23PriceDiffVolatility(FutureFactor):
    '''
    Description: -std(close_02 / close_03 - 1, 30)
    Class: All_Contract
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Other_Future_Instrument'] = {'02': ['close'], '03': ['close']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close_02 = data['close_02'].values[-30:]
        close_03 = data['close_03'].values[-30:]
        f = -np.nanstd((close_02 - close_03) / close_03)
        return f
