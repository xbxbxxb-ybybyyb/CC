import numpy as np
from future_factor import FutureFactor

class MinutePVCorr15Bias120(FutureFactor):
    '''
    Description: -z_score(corr(volume, close, 15), 120)
    Class: PV_corr
    Author: liuz, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Future_Data'] = ['close', 'volume']
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    
    def rolling_corr(self, data_1, data_2, window):
        assert len(data_1)==len(data_2), 'length of two arrays must be the same! ({}, {})'.format(len(data_1), len(data_2))
        rolling_corr = np.array([])
        for i in range(len(data_1) - window + 1):
            rolling_corr = np.append(rolling_corr, np.corrcoef(data_1[i:i+window], data_2[i:i+window])[0, 1])
        return rolling_corr
    
    def calculate(self, data):
                
        close = data['close'].values
        volume = data['volume'].values
        
        pv_corr = self.rolling_corr(close, volume, 15)
        
        f = - (pv_corr[-1] - np.nanmean(pv_corr[-120:])) / np.nanstd(pv_corr[-120:])
        
        return f