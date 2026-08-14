import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class MinuteEODVolumeWeightedReturnSharpe(BaseFactor):
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute"]
    reform_window = 20

    def calc_single(self, database):
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        stk_code = close.columns
        close, vol = close.values, vol.values
        ret = close[1:] / close[:-1] - 1
        vol_last = np.nanmean(ret[-15:] * vol[-15:] / np.nansum(vol[-15:], axis=0), axis=0)
        result = pd.Series(-vol_last, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(20, min_periods=1).mean() / temp_result.rolling(20, min_periods=1).std()
        return alpha
