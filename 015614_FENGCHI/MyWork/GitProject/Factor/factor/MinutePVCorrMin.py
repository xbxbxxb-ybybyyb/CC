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


class MinutePVCorrMin(BaseFactor):
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute",
                   "FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.volume_minute"]
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=['drop', 'merge'])
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        low = database.depend_data['FactorData.Basic_factor.low_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        p = (amt.rolling(15).sum().values / vol.rolling(15).sum().values)[15:]
        d = (high.rolling(15).max().values - low.rolling(15).min().values)[15:]
        corr = array_corr_np(p, d)
        result = pd.Series(-corr, index=high.columns)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(self.reform_window).min()
        return alpha
