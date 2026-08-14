import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor


def array_corr_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    numerator = np.nanmean(d_x * d_y, axis=0)
    denominator = np.nanstd(x, axis=0) * np.nanstd(y, axis=0)
    corr = numerator / denominator
    corr[np.isinf(corr)] = np.nan
    return corr


class GTJA_083(BaseFactor):
    depend_data = ['FactorData.Basic_factor.high', 'FactorData.Basic_factor.volume',
                   'FactorData.Basic_factor.adjfactor', 'FactorData.Basic_factor.is_valid']
    lag = 4

    def calc_single(self, database):
        high = database.depend_data['FactorData.Basic_factor.high']
        vol = database.depend_data['FactorData.Basic_factor.volume']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        valid = database.depend_data['FactorData.Basic_factor.is_valid']
        stk_code = high.columns
        high, vol, adj, valid = high.values, vol.values, adj.values, valid.values[-1]
        high = pd.DataFrame(high * adj).rank(pct=True, axis=1).values
        vol = pd.DataFrame(vol / adj).rank(pct=True, axis=1).values
        corr = array_corr_np(high, vol)
        alpha = pd.Series(corr).rank(pct=True).values
        alpha[np.isinf(alpha)] = np.nan
        alpha[valid == 0] = np.nan
        alpha = pd.Series(alpha, index=stk_code)
        return -alpha
