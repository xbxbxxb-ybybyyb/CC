import numpy as np
from future_factor import FutureFactor

class MinuteWeightedConsensusUpDownRatio(FutureFactor):
    '''
    Description: (weighted_up_count - weighted_down_count) / (weighted_up_count + weighted_down_count),
weighted_up_count = sum(where(Contract0[-30:] > Contract0[-31: -1] & ... & Contract3[-30:] > Contract3[-31: -1], range(1, 31), nan)),
weighted_down_count = sum(where(Contract0[-30:] < Contract0[-31: -1] & ... & Contract3[-30:] < Contract3[-31: -1], range(1, 31), nan))
    Class: MTM
    Author: hefj, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Other_Future_Instrument'] = {'00':['close'], '01':['close'], '02':['close'], '03':['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        index_close = data['close_000905.SH'].values
        close_00 = data['close_00'].values
        close_01 = data['close_01'].values
        close_02 = data['close_02'].values
        close_03 = data['close_03'].values
        
        N = 30
        w = np.arange(1, N+1)
        up_0 = close_00[-N:] > close_00[-N-1:-1]
        up_1 = close_01[-N:] > close_01[-N-1:-1]
        up_2 = close_02[-N:] > close_02[-N-1:-1]
        up_3 = close_03[-N:] > close_03[-N-1:-1]
        up_index = index_close[-N:] > index_close[-N-1:-1]
        w_up = w[up_0 & up_1 & up_2 & up_3 & up_index].sum()
        w_down = w[~(up_0 | up_1 | up_2 | up_3 | up_index)].sum()
        f = (w_up - w_down) / (w_up + w_down)
        if np.isnan(f) or np.isinf(f):
            f = 0
        
        return f