from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class Minute60CloseStdMeanRatio(FutureFactor):
    '''
    Description: std(Index_ClosePx,60) / mean(Index_ClosePx,60)
    Class: Volatility
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH': ['close']}
    normalize_size = 30 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 60
        close = data['close_000905.SH'].values[-n:]

        return np.nanstd(close) / np.nanmean(close)