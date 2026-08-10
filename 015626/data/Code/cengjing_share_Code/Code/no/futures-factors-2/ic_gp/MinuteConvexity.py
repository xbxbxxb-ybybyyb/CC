import numpy as np
from future_factor import FutureFactor

class MinuteConvexity(FutureFactor):
    '''
    Description: mean(convexity(close_000905.SH, i), i=3,5,…119)
    Class: Price_Stat
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 120
        close = data['close_000905.SH'].values
        close[close == 0] = np.nan
        close = close[-lb:]
        close = close[~np.isnan(close)]
        
        convex = []
        for i in range(3, len(close), 2):
            convex.append(abs((close[-1] + close[-i] - 2 * close[-int((i + 1) / 2)]) / close[-int((i + 1) / 2) - 1]))
       
        return np.nanmean(convex)