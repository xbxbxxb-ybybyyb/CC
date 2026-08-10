import numpy as np
from future_factor import FutureFactor

class MinuteCloseminusOpenStd_Refined(FutureFactor):
    '''
    Description: 
    Class: Price_Stat 
    Author: jinpx, modified by liuz
    '''
    def __init__(self):
        super().__init__()
        self.rolling_std = []

    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 5
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['close', 'open']}
    normalize_size = 3 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):

        close_price = data['close_cont_IC'].values
        open_price = data['open_cont_IC'].values
        close_minus_open = close_price - open_price
        
        N1 = 30
        N2 = 5*240
        if len(self.rolling_std) == 0:
            for i in range(N2, -1, -1):
                self.rolling_std.append(np.nanstd(close_minus_open[-(i+N1):][:N1]))
        else:
            self.rolling_std.append(np.nanstd(close_minus_open[-N1:]))

        f = (self.rolling_std[-1] - np.nanmean(self.rolling_std[-(N2+1):-1])) / np.nanstd(self.rolling_std[-(N2+1):-1])

        return f