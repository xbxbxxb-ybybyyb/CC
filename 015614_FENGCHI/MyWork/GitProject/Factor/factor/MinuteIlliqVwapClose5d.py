import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


def decay(x):
    period = len(x)
    decay_days = 5.0
    w = np.array([pow(pow(1 / 2, 1 / decay_days), period - 1 - i) for i in range(period)])
    w = w / sum(w)
    return np.sum(w * x)


class MinuteIlliqVwapClose5d(BaseFactor):
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.volume_minute",
                   "FactorData.Basic_factor.close_minute"]
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=['merge', 'merge'])
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        stk_code = amt.columns
        close_5min = close.resample('5min').last().dropna(how='all')
        amt_5min = amt.resample('5min').sum().loc[close_5min.index].values
        vol_5min = vol.resample('5min').sum().loc[close_5min.index].values
        close_5min = close_5min.values
        close = close.values
        re = close_5min[1:] / close_5min[:-1] - 1
        illiq = np.abs(re) / amt_5min[1:]
        zscore = (illiq - np.nanmean(illiq, axis=0)) / np.nanstd(illiq, axis=0)
        vwap = np.nansum(np.where(zscore > 2, amt_5min[1:], np.nan), axis=0) / np.nansum(
            np.where(zscore > 2, vol_5min[1:], np.nan), axis=0)
        result = 1 - close[-1] / vwap
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        temp_result = temp_result.fillna(0)
        alpha = temp_result.rolling(10, min_periods=1).apply(decay)
        return alpha
