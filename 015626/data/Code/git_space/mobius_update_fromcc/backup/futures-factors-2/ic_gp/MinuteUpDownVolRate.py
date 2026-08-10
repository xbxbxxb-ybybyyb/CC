import numpy as np
from future_factor import FutureFactor

class MinuteUpDownVolRate(FutureFactor):
    '''
    Description: sum(where(index_close >= delay(index_close, 1), index_volume, 0), 60) / sum(index_volume, 60)
    Class: MTM
    Author: liuz, modified by jinpx
    '''   
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'volume']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        index_close = data['close_000905.SH'].values[-60:]
        index_volume = data['volume_000905.SH'].values[-60:]
        
        index_r = np.append(np.nan, np.diff(index_close) / index_close[:-1])
        f = np.nansum(index_volume[index_r>=0]) / np.nansum(index_volume)        
        
        return f