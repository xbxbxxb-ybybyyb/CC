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

class LiqCorr(BaseFactor):
    depend_data = ["FactorData.Basic_factor.volume", "FactorData.Basic_factor.free_float_shares",
                   "FactorData.Basic_factor.vwap", "FactorData.Basic_factor.adjfactor"]
    lag = 20

    def calc_single(self, database):
        volume = database.depend_data['FactorData.Basic_factor.volume']
        free_float_shares = database.depend_data['FactorData.Basic_factor.free_float_shares']
        vwap = database.depend_data['FactorData.Basic_factor.vwap']
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        stk_code = volume.columns
        volume, vwap, adjfactor, free_float_shares = 100 * volume.values[-self.lag:],vwap.values[-self.lag-1:],\
        adjfactor.values[-self.lag-1:], 10000 * free_float_shares.values[-self.lag:]
        liq = volume / free_float_shares
        vwap = vwap * adjfactor / adjfactor[-1]
        r = vwap[1:] / vwap[:-1] - 1
        corr = array_corr_np(liq, r)
        liq_corr = pd.Series(-1 * liq[-1] * corr, index=stk_code)
        return liq_corr
