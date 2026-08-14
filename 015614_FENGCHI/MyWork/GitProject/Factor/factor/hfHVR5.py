import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


def rolling_ewm(df, n):
    seq = [(1 - (1.5 / (n + 1))) ** (n - i) for i in range(1, n + 1)]
    weight = np.array(seq)
    return df.rolling(n).apply(lambda x: np.nansum(x * weight) / max(weight[np.isnan(x)].sum(), 1. / n))


class hfHVR5(BaseFactor):
    depend_data = ['FactorData.Basic_factor.volume_minute', 'FactorData.Basic_factor.amt_minute']
    reform_window = 5
    factor_type = 'FIX'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        stk_code = vol.columns
        vol, amt = vol.values, amt.values
        vwap = amt / vol
        vrs_flag = vol >= np.nanquantile(vol, 0.9, axis=0)
        result = np.nanmean(np.where(vrs_flag, vwap, np.nan), axis=0) / np.nanmean(vwap, axis=0)
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = -rolling_ewm(temp_result, 5)
        return alpha
