from future_factor import FutureFactor
import numpy as np


class MinuteHighLowCorr_IF_IH(FutureFactor):
    '''
    Description: corr(high_000300.SH, low_000300.SH, 30)
    Class: Price_Stat
    Author: hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000016.SH': ['high', 'low']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        high = data['high_000016.SH'].values[-30:]
        low = data['low_000016.SH'].values[-30:]
        f = np.corrcoef(high, low)[0, 1]
        return f
