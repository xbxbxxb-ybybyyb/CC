from future_factor import FutureFactor
import numpy as np


class MinuteTypicalFutureIndexCorr(FutureFactor):
    '''
    Description: corr((close + high + low) / 3, (close_000905.SH + high_000905.SH + low_000905.SH) / 3, 45)
    Class: Future_Spot_Price
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = {}
    data_dict['Future_Data'] = ['close', 'high', 'low']
    data_dict['Index_Id'] = {'000905.SH': ['close', 'high', 'low']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        typical = (data['close'].values[-45:] + data['high'].values[-45:] + data['low'].values[-45:]) / 3
        index_typical = (data['close_000905.SH'].values[-45:] + data['high_000905.SH'].values[-45:] + data['low_000905.SH'].values[-45:]) / 3
        f = np.corrcoef(typical, index_typical)[0, 1]
        return f
