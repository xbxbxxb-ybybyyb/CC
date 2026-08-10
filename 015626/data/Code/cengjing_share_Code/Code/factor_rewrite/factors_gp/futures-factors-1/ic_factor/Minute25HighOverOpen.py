from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class Minute25HighOverOpen(FutureFactor):
    '''
    Description: -mean(Index_HighPx, 25) / mean(Index_OpenPx, 25)
    Class: MTM
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH': ['high', 'open']}
    normalize_size = 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 25
        index_high = data['high_000905.SH'].values[-n:]
        index_open = data['open_000905.SH'].values[-n:]

        return np.nanmean(index_high) / np.nanmean(index_open)