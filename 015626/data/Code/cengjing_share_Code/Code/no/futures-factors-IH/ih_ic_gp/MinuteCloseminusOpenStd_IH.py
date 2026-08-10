import numpy as np
import pandas as pd
from future_factor import FutureFactor


    
class MinuteCloseminusOpenStd_IH(FutureFactor):
    '''
    Description: (std(ClosePx - OpenPx, 30) - mean(std(ClosePx - OpenPx, 30), 240)) / std(std(ClosePx - OpenPx, 30), 240)
    Class: Price_Stat
    Author:  jinpx modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=5
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IH': ['close', 'open']}
    
    normalize_size=10*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        close = data['close_cont_IH'].values 
        open_ = data['open_cont_IH'].values 

        N1 = 30
        N2 = 720
        rolling_std = []
        for i in range(720,-1, -1):

            rolling_std.append(np.nanstd((close-open_)[-N1-i:][:N1]))
        factor = (rolling_std[-1] - np.mean(rolling_std[-(N2+1):-1])) / np.std(rolling_std[-(N2+1):-1])

    
        return factor
    
    