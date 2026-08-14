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


class hfLowCapRetMax(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_adj_minute', 'FactorData.Basic_factor.volume_adj_minute',
                   'FactorData.Basic_factor.low_adj_minute', 'FactorData.Basic_factor.amt_minute']
    lag = 1
    reform_window = 10
    factor_type = 'FIX'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        low = database.depend_data['FactorData.Basic_factor.low_adj_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        stk_code = close.columns
        close, vol, low, amt = close.values[-240:], vol.values[-240:], low.values[-240:], amt.values[-240:]
        vwap = amt / vol
        flag = vwap[1:] < vwap[:-1]
        low_cap = low * vol
        low_ret = close[-1] / low - 1
        result = array_corr_np(np.where(flag, low_cap[1:], np.nan), np.where(flag, low_ret[1:], np.nan))
        result[np.isinf(result)] = np.nan
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result / (-temp_result).rolling(10, 1).max()
        alpha[alpha.isnull().all(axis=1)] = 0
        return alpha
