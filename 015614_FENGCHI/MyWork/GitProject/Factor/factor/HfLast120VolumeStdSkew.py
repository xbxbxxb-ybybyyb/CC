from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class HfLast120VolumeStdSkew(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.volume_adj_minute"]
    lag = 1

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        volume = database.depend_data['FactorData.Basic_factor.volume_adj_minute']

        minute_volume = volume.iloc[-240:]
        minute_volume_std = minute_volume.rolling(window=5,min_periods=1).std()        
        ans = - minute_volume_std.iloc[-120:].skew()
        ans[~np.isfinite(ans)] = np.nan
        return ans