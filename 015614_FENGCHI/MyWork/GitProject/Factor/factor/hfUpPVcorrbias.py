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


class hfUpPVcorrbias(BaseFactor):
    depend_data = ['FactorData.Basic_factor.volume_minute', 'FactorData.Basic_factor.amt_minute']
    reform_window = 10
    factor_type = 'FIX'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        stk_code = amt.columns
        amt, vol = amt.values, vol.values
        vwap = amt / vol
        rs_flag = vwap[1:] > vwap[:-1]
        result = array_corr_np(np.where(rs_flag, vol[1:], np.nan), np.where(rs_flag, vwap[1:], np.nan))
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        bs = (temp_result - temp_result.rolling(5).mean()) / temp_result.rolling(5).std()
        alpha = -bs.rolling(5, 1).mean()
        return alpha
