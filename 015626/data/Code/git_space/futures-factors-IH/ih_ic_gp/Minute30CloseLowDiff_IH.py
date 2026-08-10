import numpy as np
import pandas as pd
from future_factor import FutureFactor

class Minute30CloseLowDiff_IH(FutureFactor):
    '''
    Description: mean(ClosePx, 30) / mean(LowPx, 30)
    Class: MTM
    Author: hefj, modeified by liuz
    '''

    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IH': ['close', 'low']}

    normalize_size=20*240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb=30
        factor = np.nanmean(data['close_cont_IH'].values[-lb:])- np.nanmean(data['low_cont_IH'].values[-lb:])
            
        return factor
