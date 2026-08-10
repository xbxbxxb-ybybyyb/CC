from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class Minute90RetAutoCorr(FutureFactor):
    '''
    Description: corr(pct_chg(Index_ClosePx,1), delay(pct_chg(Index_ClosePx,1),1),90)
    Class: AutoCorr
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH': ['close']}
    normalize_size = 40 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n1 = 1
        n2 = 90
        index_close = data['close_000905.SH'].values[-(n2 + 1):]

        rtn = index_close[1:] / index_close[:-1] - 1

        return np.corrcoef(rtn[n1:], rtn[:-n1])[0, 1]