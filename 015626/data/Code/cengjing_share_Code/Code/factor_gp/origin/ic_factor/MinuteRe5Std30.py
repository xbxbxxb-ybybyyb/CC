import numpy as np
from future_factor import FutureFactor

class MinuteRe5Std30(FutureFactor):
    '''
    Description: std(pct_chg(close, 5), 30)
    Class: Price_Stat
    Author: liuz, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Future_Data'] = ['close']
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close'].values
        
        r_5 = (close[5:] - close[:-5]) / close[:-5]
        f = np.nanstd(r_5[-30:], ddof=1)
        
        return f