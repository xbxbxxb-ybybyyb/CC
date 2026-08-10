import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteSwing5Mean60(FutureFactor):
    '''
    Description: mean((max(close, 5) - min(close, 5)) / delay(close, 5), 60)
    Class: Price_Stat
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Future_Data'] = ['close']
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        close = data['close'].values
        
        swing_5 = (bn.move_max(close, 5) - bn.move_min(close, 5))[5:] / close[:-5]

        N = 60
        f = np.nanmean(swing_5[-N:])
        
        return f