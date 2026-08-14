from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd


def array_corr_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    numerator = np.nanmean(d_x * d_y, axis=0)
    denominator = np.nanstd(x, axis=0) * np.nanstd(y, axis=0)
    corr = numerator / denominator
    corr[np.isinf(corr)] = np.nan
    return corr


class CumPVRatioCorr(BaseFactor):
    depend_data = ['FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.volume_adj_minute']
    factor_type = 'FIX'
    lag = 1

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        stk_code = amt.columns
        amt, vol = amt.values, vol.values
        l = len(amt) - 240
        p_0 = np.nancumsum(amt[:l], axis=0) / np.nancumsum(vol[:l], axis=0)
        p_1 = np.nancumsum(amt[240:240+l], axis=0) / np.nancumsum(vol[240:240+l], axis=0)
        p = p_1 / p_0
        v_0 = np.nancumsum(vol[:l], axis=0)
        v_1 = np.nancumsum(vol[240:240+l], axis=0)
        v = v_1 / v_0
        result = pd.Series(-array_corr_np(p, v), index=stk_code)
        return result
