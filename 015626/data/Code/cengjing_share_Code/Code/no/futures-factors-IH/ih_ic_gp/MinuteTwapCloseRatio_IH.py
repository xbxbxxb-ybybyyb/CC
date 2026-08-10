from future_factor import FutureFactor
import numpy as np


class MinuteTwapCloseRatio_IH(FutureFactor):
    '''
    Description: -mean(twap, 30) / mean(close, 30)
    Class: MTM
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Continuous_Data'] = {'IH':['close', 'twap']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close_cont_IH'].values[-30:]
        twap = data['twap_cont_IH'].values[-30:]
        f = -np.mean(twap) / np.mean(close)
        return f
