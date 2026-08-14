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


class HighVolCorrStd(BaseFactor):
    depend_data = ["FactorData.Basic_factor.high", "FactorData.Basic_factor.volume", "FactorData.Basic_factor.adjfactor"]
    lag = 40

    def calc_single(self, database):
        high = database.depend_data['FactorData.Basic_factor.high']
        volume = database.depend_data['FactorData.Basic_factor.volume']
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        stk_code = high.columns
        high, volume, adjfactor = high.values[-self.lag:], volume.values[-self.lag:] * 100, adjfactor.values[-self.lag:]
        high = high * adjfactor / adjfactor[-1]
        volume = volume / adjfactor * adjfactor[-1]
        std = np.std(high, axis=0)
        corr = array_corr_np(high, volume)
        corr[(np.isnan(high) | np.isnan(volume)).sum(axis=0) > 0] = np.nan
        alpha = pd.Series(std).rank(ascending=True, pct=True).values * corr
        alpha = pd.Series(-alpha, index=stk_code)
        return alpha