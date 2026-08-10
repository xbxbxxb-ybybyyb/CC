import numpy as np
from future_factor import FutureFactor

class MinuteICIHDivergenceCount_IH(FutureFactor):
    '''
    Description: sum(where((close_000905.SH > shift(close_000905.SH, 1)) & (close_000016.SH < shift(close_000016.SH, 1)), weight, 0), 20)
                - sum(where((close_000905.SH < shift(close_000905.SH, 1)) & (close_000016.SH > shift(close_000016.SH, 1)), weight, 0), 20),
                weight = range(1, 21)
    Class: Multi-Variety
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close'], '000016.SH':['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 20
        w = np.arange(1, lb + 1)
        close = data['close_000905.SH'].values
        close[close == 0] = np.nan
        close_1 = data['close_000016.SH'].values
        close_1[close_1 == 0] = np.nan
        
        up_down = (close[-lb:] > close[-lb - 1: -1]) & (close_1[-lb:] < close_1[-lb - 1: -1])
        down_up = (close[-lb:] < close[-lb - 1: -1]) & (close_1[-lb:] > close_1[-lb - 1: -1])
        f = w[up_down].sum() - w[down_up].sum()
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f