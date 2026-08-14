from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class MinuteLastTurn20std(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.float_a_shares", "FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.is_valid"]
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])
        float_a_shares = database.depend_data['FactorData.Basic_factor.float_a_shares']
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']

        float_a_shares = float_a_shares.replace(0.,np.nan)
        ans = np.nansum(volume.values[-5:], axis=0) / float_a_shares.values[0]
        ans = pd.Series(ans, index=volume.columns)
        ans[is_valid.iloc[-1]==0] = np.nan
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        return - temp_result.rolling(self.reform_window, min_periods=1).std()

    