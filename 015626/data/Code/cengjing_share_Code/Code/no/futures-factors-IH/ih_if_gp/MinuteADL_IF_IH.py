from future_factor import FutureFactor
import numpy as np


class MinuteADL_IF_IH(FutureFactor):
    '''
    Description: mean((ClosePx - OpenPx) / (HighPx - LowPx), 120)
    Class: MTM
    Author:jinpx,  modeified by liuz
    '''
    data_type='Future'
    instrument_type='recent'
    days_past=1
    data_dict=dict()
    data_dict['Index_Id'] ={'000016.SH':['close','low', 'open', 'high']}

    normalize_size= 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        lb=120
        factor =(data['close_000016.SH'].values[-lb:]-data['open_000016.SH'].values[-lb:])/(data['high_000016.SH'].values[-lb:]-data['low_000016.SH'].values[-lb:])

        return np.nanmean(factor)
