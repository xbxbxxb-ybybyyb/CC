import numpy as np
import pandas as pd
from future_factor import FutureFactor

class MinuteADL_IH(FutureFactor):
    '''
    Description: mean((ClosePx - OpenPx) / (HighPx - LowPx), 120)
    Class: MTM
    Author:jinpx,  modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Continuous_Data'] = {'IH': ['close', 'low', 'open', 'high']}

    normalize_size=1*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb=120
        factor =(data['close_cont_IH'].values[-lb:]-data['open_cont_IH'].values[-lb:])/(data['high_cont_IH'].values[-lb:]-data['low_cont_IH'].values[-lb:])
            
        return np.nanmean(factor)
