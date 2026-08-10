from scipy import stats
import pandas as pd
import numpy as np
from future_factor import FutureFactor


class Minute25OBV(FutureFactor):
    '''
    Description: sum(where(Index_ClosePx > delay(Index_ClosePx,1), Index_Volume, 0), 25) / sum(Index_Volume, 25)
    Class: MTM
    Author: lixr, modified by shentq
    '''
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH': ['close', 'volume']}
    normalize_size = 15 * 240
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 25
        index_close = data['close_000905.SH'].values[-(n + 1):]
        index_volume = data['volume_000905.SH'].values[-(n + 1):]

        rtn = index_close[1:] / index_close[:-1] - 1
        rtn = np.insert(rtn, 0, np.nan)

        up_vol_sum = np.nansum(index_volume[rtn > 0])
        up_vol_ratio = up_vol_sum / np.nansum(index_volume)

        return up_vol_ratio