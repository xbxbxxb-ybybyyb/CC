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


class hfHighCapRetMean(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.volume_minute',
                   'FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.high_minute']
    reform_window = 5
    factor_type = 'FIX'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        stk_code = close.columns
        close, vol, amt, high = close.values, vol.values, amt.values, high.values
        vwap = amt / vol
        flag = vwap[1:] > vwap[:-1]
        high_cap = high * vol
        high_ret = close[-1] / high - 1
        result = array_corr_np(np.where(flag, high_ret[1:], np.nan), np.where(flag, high_cap[1:], np.nan))
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = -temp_result / temp_result.rolling(5, 1).mean()
        return alpha
