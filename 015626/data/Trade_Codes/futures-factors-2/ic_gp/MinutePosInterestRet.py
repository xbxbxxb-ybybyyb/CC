from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class MinutePosInterestRet(FutureFactor):
    '''
    Description:
    Class: PV_Corr
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['interest', 'close']}
    normalize_size = 15 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 30

        interest = data['interest_cont_IC'].values[-n:]
        close = data['close_cont_IC'].values[-n - 1:]

        rtn = close[1:] / close[:-1] - 1

        factor_value = np.nanmean(rtn[interest > 0])

        if np.isinf(factor_value) or np.isnan(factor_value):
            factor_value = 0

        return factor_value