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


class MinuteCorrRank(BaseFactor):
    depend_data = ['FactorData.Basic_factor.high', 'FactorData.Basic_factor.volume',
                   'FactorData.Basic_factor.high_minute', 'FactorData.Basic_factor.low_minute']
    lag = 4

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        high_min = database.depend_data['FactorData.Basic_factor.high_minute'].iloc[-240:]
        low_min = database.depend_data['FactorData.Basic_factor.low_minute'].iloc[-240:]
        high = database.depend_data['FactorData.Basic_factor.high']
        vol = database.depend_data['FactorData.Basic_factor.volume']
        stk_code = high.columns.union(high_min.columns)
        high_min = high_min.reindex(columns=stk_code)
        low_min = low_min.reindex(columns=stk_code)
        high = high.reindex(columns=stk_code)
        vol = vol.reindex(columns=stk_code)
        temp = vol.rank(axis=1, pct=True).values[-5:]
        high = high.values[-5:]
        alpha_day = array_corr_np(temp, high)
        alpha_day[np.isinf(alpha_day)] = np.nan

        wave30 = np.nanmax(high_min.values[-30:], axis=0) - np.nanmin(low_min.values[-30:], axis=0)
        wave = np.nanmax(high_min.values, axis=0) - np.nanmin(low_min.values, axis=0)
        intraday = wave30 / wave
        a = pd.Series(alpha_day).rank().values
        b = pd.Series(intraday).rank().values
        alpha = pd.Series(-(a + b), index=stk_code)
        return alpha
