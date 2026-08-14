import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


def ewm(x):
    window = len(x)
    seq = [(1 - (2.0 / (window + 1))) ** (window - i) for i in range(1, window + 1)]
    weight = np.array(seq)
    weight_sum = np.sum(weight)
    return np.nansum(x * weight) / weight_sum


class MinTopVolRate(BaseFactor):
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute"]
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['merge', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        stk_code = close.columns
        close, vol = close.values, vol.values
        r = (close[1:] / close[:-1] - 1)[-60:]
        vol = vol[-60:]
        r_rank = pd.DataFrame(r).rank(axis=0, pct=True).values
        result = (np.nansum(np.where(r_rank > 0.3, vol, np.nan), axis=0) - np.nansum(
            np.where(r_rank < 0.3, vol, np.nan), axis=0)) / np.nansum(vol, axis=0)
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = -temp_result.rolling(self.reform_window, min_periods=1).apply(lambda x: ewm(x))
        return alpha
