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


class MinVVCorrRank(BaseFactor):
    depend_data = ['FactorData.Basic_factor.volume_minute', 'FactorData.Basic_factor.close_minute',
                   'FactorData.Basic_factor.vwap', 'FactorData.Basic_factor.volume',
                   'FactorData.Basic_factor.adjfactor']
    lag = 4
    minute_lag = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        vwap = database.depend_data['FactorData.Basic_factor.vwap']
        vol = database.depend_data['FactorData.Basic_factor.volume']
        vol_min = database.depend_data['FactorData.Basic_factor.volume_minute']
        close_min = database.depend_data['FactorData.Basic_factor.close_minute']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        stk_code = vwap.columns
        vwap = vwap.values * adj.values / adj.values[-1]
        vol = vol.values / adj.values * adj.values[-1]
        corr = array_corr_np(vwap, vol)
        corr_rank_0 = pd.Series(corr).rank(pct=True).values
        corr = array_corr_np(close_min.values[-30:], vol_min.values[-30:])
        corr_rank_1 = pd.Series(corr).rank(pct=True).values
        result = pd.Series(-corr_rank_0 * corr_rank_1, index=stk_code)
        return result
