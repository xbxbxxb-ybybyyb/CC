import numpy as np
from future_factor import FutureFactor

class MinuteBounceZScore240(FutureFactor):
    '''
    Description: z_score(close - cum_min(low) / cum_min(low), 240)
    Class: Return_Risk
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['close','low']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 240
        close = data['close_cont_IC'].values
        close[close == 0] = np.nan
        close_temp = close[-lb:]
        low = data['low_cont_IC'].values
        low[low == 0] = np.nan
        low_temp = low[-lb:]
        mask = np.isnan(close_temp) | np.isnan(low_temp)
        close_temp = close_temp[~mask]
        low_temp = low_temp[~mask]
        
        price_min = np.minimum.accumulate(low_temp)
        bounce = (close_temp - price_min) / price_min
            
        return (bounce[-1] - np.mean(bounce)) / np.std(bounce)