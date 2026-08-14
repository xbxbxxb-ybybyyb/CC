from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class MinuteVolumeStabilitySharpe(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.volume_minute"]
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']

        volume_5min = volume.groupby(pd.Grouper(freq='5min')).sum().dropna(how ='all')
        volume_5min = volume_5min[~((volume_5min.index.hour==11) & (volume_5min.index.minute>25) | (volume_5min.index.hour ==12))]
        ans = np.nanstd(volume_5min.values, axis=0, ddof=1) / np.nanmean(volume_5min.values, axis=0)
        ans = pd.Series(ans, index=volume.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window, min_periods=1).mean() / temp_result.rolling(self.reform_window, min_periods=1).std()



