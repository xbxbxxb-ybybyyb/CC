import numpy as np
from future_factor import FutureFactor

class MinuteRe5Autocorr5_60Std120(FutureFactor):
    '''
    Description: std(corr(pct_chg(index_close, 5), delay(pct_chg(index_close, 5), 5), 60), 60)
    Class: Price_Stat
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def rolling_corr(self, data_1, data_2, window):
        assert len(data_1)==len(data_2), 'length of two arrays must be the same! ({}, {})'.format(len(data_1), len(data_2))
        rolling_corr = np.array([])
        for i in range(len(data_1) - window + 1):
            rolling_corr = np.append(rolling_corr, np.corrcoef(data_1[i:i+window], data_2[i:i+window])[0, 1])
        return rolling_corr
    
    def calculate(self, data):
                
        index_close = data['close_000905.SH'].values
        index_r_5 = (index_close[5:] - index_close[:-5]) / index_close[:-5]
        index_r_5_autocorr_5 = self.rolling_corr(index_r_5[5:], index_r_5[:-5], 60)
        f = np.nanstd(index_r_5_autocorr_5[-60:], ddof=1)
        
        return f