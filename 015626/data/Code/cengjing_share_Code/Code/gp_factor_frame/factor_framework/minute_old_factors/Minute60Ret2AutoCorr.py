from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class Minute60Ret2AutoCorr(FutureFactor):
    '''
    Description: corr(pct_chg(Index_ClosePx,1), delay(pct_chg(Index_ClosePx,1),2), 60)
    Class: AutoCorr
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH': ['close']}
    normalize_size = 30 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n1 = 2
        n2 = 60
        index_close = data['close_000905.SH'].values[-n2 - 1:]
        rtn = index_close[1:] / index_close[:-1] - 1

        rtn_shift_2 = rtn[n1:]

        return np.corrcoef(rtn[:-n1], rtn_shift_2)[0, 1]