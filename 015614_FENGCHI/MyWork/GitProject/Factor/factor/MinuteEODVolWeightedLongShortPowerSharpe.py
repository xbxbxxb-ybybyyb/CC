import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class MinuteEODVolWeightedLongShortPowerSharpe(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.volume_minute']
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        stk_code = close.columns
        ret, vol = close.pct_change().values[-60:], vol.values[-60:]
        long = np.nansum(np.where(ret > 0, ret * vol, np.nan), axis=0)
        short = np.nansum(np.where(ret < 0, ret * vol, np.nan), axis=0)
        result = pd.Series(-(long + short) / np.nansum(vol, axis=0), index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(10, 1).mean() / temp_result.rolling(10, 1).std()
        return alpha
