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


class CorrMaxRePrice5minSharpe(BaseFactor):
    factor_type = 'FIX'
    depend_data = ['FactorData.Basic_factor.high_minute', 'FactorData.Basic_factor.low_minute',
                   'FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.open_minute']
    lag = 4

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        low = database.depend_data['FactorData.Basic_factor.low_minute']
        op = database.depend_data['FactorData.Basic_factor.open_minute']
        stk_code = op.columns
        result = np.nan * np.ones((5, len(stk_code)))
        for i in range(5):
            high_temp = high.iloc[i*240:(i+1)*240].rolling(5, 4).max().values
            low_temp = low.iloc[i*240:(i+1)*240].rolling(5, 4).min().values
            close_temp = close.iloc[i*240:(i+1)*240].values
            open_temp = op.iloc[i*240:(i+1)*240].shift(5).values
            r_1 = (close_temp - low_temp + high_temp - open_temp) / open_temp
            r_2 = (high_temp - close_temp + open_temp - low_temp) / open_temp
            r = np.where(close_temp < open_temp, r_2, r_1)
            c_mean = close.iloc[i*240:(i+1)*240].rolling(5, 4).mean().values
            result[i] = -array_corr_np(r, c_mean)
        result = pd.Series(np.nanmean(result, axis=0) / np.nanstd(result, axis=0), index=stk_code)
        return result
