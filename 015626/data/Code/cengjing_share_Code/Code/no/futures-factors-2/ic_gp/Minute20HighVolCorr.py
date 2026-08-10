from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class Minute20HighVolCorr(FutureFactor):
    '''
    Description: -corr(volume, high, 20)
    Class: PV_Corr
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high', 'volume']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        high = data['high_cont_IC'].values[-20:]
        volume = data['volume_cont_IC'].values[-20:]

        return -np.corrcoef(high, volume)[0, 1]