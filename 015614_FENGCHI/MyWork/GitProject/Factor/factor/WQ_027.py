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


class WQ_027(BaseFactor):
    depend_data = ["FactorData.Basic_factor.vwap", "FactorData.Basic_factor.volume", "FactorData.Basic_factor.adjfactor"]
    lag = 6

    def calc_single(self, database):
        vwap = database.depend_data['FactorData.Basic_factor.vwap']
        volume = database.depend_data['FactorData.Basic_factor.volume']
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        stk_code = vwap.columns
        vwap, volume, adjfactor = vwap.values[-self.lag:], volume.values[-self.lag:], adjfactor.values[-self.lag:]
        vwap, volume = vwap * adjfactor / adjfactor[-1], volume / adjfactor * adjfactor[-1]
        corr = array_corr_np(vwap, volume)
        corr[(~(np.isnan(vwap) | np.isnan(volume))).sum() < 3] = np.nan
        alpha = pd.Series(-corr, index=stk_code)
        return alpha
