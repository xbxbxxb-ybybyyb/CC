import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


def array_corr_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    numerator = np.nanmean(d_x * d_y, axis=0)
    denominator = np.nanstd(x, axis=0) * np.nanstd(y, axis=0)
    corr = numerator / denominator
    corr[np.isinf(corr)] = np.nan
    return corr


class hfUpRRC(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.volume_minute',
                   'FactorData.Basic_factor.low_minute', 'FactorData.Basic_factor.high_minute',
                   'FactorData.Basic_factor.amt_minute']
    lag = 1
    factor_type = 'FIX'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        low = database.depend_data['FactorData.Basic_factor.low_minute']
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        stk_code = close.columns
        close = close.values[-240:]
        vol = vol.values[-240:]
        low = low.values[-240:]
        high = high.values[-240:]
        amt = amt.values[-240:]
        vwap = amt / vol
        swing = high - low
        ret = vwap[1:] / vwap[:-1] - 1
        rs_flag = close[1:] > close[:-1]
        result = array_corr_np(np.where(rs_flag, swing[1:], np.nan), np.where(rs_flag, ret, np.nan))
        result = pd.Series(-result, index=stk_code)
        return result
