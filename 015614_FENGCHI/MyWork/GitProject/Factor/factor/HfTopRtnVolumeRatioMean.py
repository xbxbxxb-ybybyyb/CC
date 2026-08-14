from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class HfTopRtnVolumeRatioMean(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.close_adj_minute", "FactorData.Basic_factor.volume_adj_minute"]
    lag = 1
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"]) 
        close = database.depend_data['FactorData.Basic_factor.close_adj_minute']       
        volume = database.depend_data['FactorData.Basic_factor.volume_adj_minute']

        minute_close = close.values[-240:]
        minute_volume = volume.values[-240:]
        minute_close_rtn = minute_close[1:] / minute_close[:-1] - 1.
        cond = minute_close_rtn > np.nanquantile(minute_close_rtn, 0.95, axis=0)
        minute_top_volume = np.where(cond, minute_volume[1:], np.nan)
        ans = - np.nanmean(minute_top_volume, axis=0) / np.nanmean(minute_volume, axis=0)  
        ans = pd.Series(ans, index=close.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean() 

