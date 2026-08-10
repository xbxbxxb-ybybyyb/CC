import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteVStd5Corr60Bias120(FutureFactor):
    '''
    Description: mean(corr(pct_chg(close, 1), volume, 15), 120) / std(corr(pct_chg(close, 1), volume, 15), 120)
    Class: PV_corr
    Author: liuz, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'volume']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def rolling_corr(self, data_1, data_2, window):
        rolling_corr = np.array([])
        for i in range(len(data_1) - window + 1):
            rolling_corr = np.append(rolling_corr, np.corrcoef(data_1[i:i+window], data_2[i:i+window])[0, 1])
        return rolling_corr
    
    def calculate(self, data):
                
        close = data['close_cont_IC'].values
        volume = data['volume_cont_IC'].values
        r = np.diff(close) / close[:-1]
        volume_sum_5 = bn.move_sum(volume, 5)
        volatility_5 = bn.move_std(r, 5)
        volume_volatility_corr = self.rolling_corr(volume_sum_5[-200:], volatility_5[-200:], 60)
        f = (volume_volatility_corr[-1] - np.nanmean(volume_volatility_corr[-120:])) / np.nanstd(volume_volatility_corr[-120:])
        if np.isnan(f):
            f = 0
        
        return f