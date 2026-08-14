from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class HighFreqDownSpeed(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.close_minute"]
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        close = database.depend_data['FactorData.Basic_factor.close_minute']

        length = close.shape[0]
        loc_max = close.fillna(-np.inf).values.argmax(axis=0)
        aroon_up = 1. - loc_max / length
        ret_min = close.values[-1] / np.nanmax(close.values, axis=0) - 1.
        ans = ret_min / aroon_up
        ans = pd.Series(ans, index=close.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        return 1. - temp_result / temp_result.rolling(self.reform_window).mean()

