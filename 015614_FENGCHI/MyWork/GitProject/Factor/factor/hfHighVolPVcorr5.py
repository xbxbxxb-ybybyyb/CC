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


def rolling_ewm(df, n):
    seq = [(1 - (1.5 / (n + 1))) ** (n - i) for i in range(1, n + 1)]
    weight = np.array(seq)
    return df.rolling(n).apply(lambda x: np.nansum(x * weight) / max(weight[np.isnan(x)].sum(), 1./n))


class hfHighVolPVcorr5(BaseFactor):
    depend_data = ['FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.volume_minute']
    factor_type = 'FIX'
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        stk_code = amt.columns
        amt, vol = amt.values, vol.values
        vwap = amt / vol
        vrs_flag = vol >= np.nanquantile(vol, 0.8, axis=0)
        result = array_corr_np(np.where(vrs_flag, vol, np.nan), np.where(vrs_flag, vwap, np.nan))
        result = pd.Series(-result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = rolling_ewm(temp_result, 5)
        return alpha
