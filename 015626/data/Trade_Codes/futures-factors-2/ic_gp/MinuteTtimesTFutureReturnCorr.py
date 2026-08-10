from future_factor import FutureFactor
import numpy as np


class MinuteTtimesTFutureReturnCorr(FutureFactor):
    '''
    Description: mean(rtn_t, 60) * corr(rtn, rtn_t, 480),
                 rtn = pct_chg(close, 1),
                 rtn_t = pct_chg(close_T, 1).
    Class: Treasure_Future
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 3
    data_dict = {}
    data_dict['Continuous_Data'] = {'IC':['close']}
    data_dict['Other_Variety'] = {'T': ['close']}
    normalize_size = 10 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        t = data['close_T'].values[-481:]
        close = data['close_cont_IC'].values[-481:]
        rtn_t = np.diff(t) / t[:-1]
        rtn = np.diff(close) / close[:-1]
        f = np.mean(rtn_t[-60:]) * np.corrcoef(rtn_t, rtn)[0, 1]
        return f
