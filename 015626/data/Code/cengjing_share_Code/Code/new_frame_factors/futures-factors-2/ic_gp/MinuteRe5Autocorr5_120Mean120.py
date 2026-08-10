import numpy as np
from future_factor import FutureFactor

class MinuteRe5Autocorr5_120Mean120(FutureFactor):
    '''
    Description: mean(corr(pct_chg(ClosePx, 5), delay(pct_chg(ClosePx, 5), 5), 120), 120)
    Class: Price_Stat
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Future_Data'] = ['close']
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def rolling_corr(self, data_1, data_2, window):
        assert len(data_1)==len(data_2), 'length of two arrays must be the same! ({}, {})'.format(len(data_1), len(data_2))
        rolling_corr = np.array([])
        for i in range(len(data_1) - window + 1):
            rolling_corr = np.append(rolling_corr, np.corrcoef(data_1[i:i+window], data_2[i:i+window])[0, 1])
        return rolling_corr
    
    def calculate(self, data):
                
        close = data['close'].values
        r_5 = (close[5:] - close[:-5]) / close[:-5]
        r_5_autocorr_5 = self.rolling_corr(r_5[5:], r_5[:-5], 120)
        f = np.nanmean(r_5_autocorr_5[-120:])
        
        return f