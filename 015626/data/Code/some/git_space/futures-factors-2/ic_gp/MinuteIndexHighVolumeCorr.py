import numpy as np
from future_factor import FutureFactor

class MinuteIndexHighVolumeCorr(FutureFactor):
    '''
    Description: abs(cs_mean(ts_corr(high, volume, 60)))
    Class: PV_Corr
    Author: jinpx, modified by jinpx
    '''
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['high', 'volume', 'adjfactor']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        N = 60
        high = data['high'].values[-N:]
        volume = data['volume'].values[-N:]
        adjfactor = data['adjfactor'].values[-N:]
        high_adj = high * adjfactor
        volume_adj = volume / adjfactor
        
        c = np.array([])
        for i in range(len(high_adj[-1])):
            c = np.append(c, np.corrcoef(high_adj[:,i], volume_adj[:,i])[0,1])
        
        f = np.abs(np.nanmean(c))
        
        return f