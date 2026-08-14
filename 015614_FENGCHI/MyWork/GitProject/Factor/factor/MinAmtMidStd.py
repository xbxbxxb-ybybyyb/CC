from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class MinAmtMidStd(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute", "FactorData.Basic_factor.volume_minute"]
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        low = database.depend_data['FactorData.Basic_factor.low_minute']
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']

        mid = (high.values + low.values) / 2.
        ans = np.nansum( (volume.values / np.nanmean(volume.values, axis=0))[1:] * (mid[1:] / mid[:-1] - 1.), axis=0) 
        ans = pd.Series(ans, index=high.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        return - temp_result.rolling(self.reform_window).std()