from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class MinBWstd(BaseFactor):  # 派生一个因子类
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute", "FactorData.Basic_factor.volume_minute"]
    reform_window = 60

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        low = database.depend_data['FactorData.Basic_factor.low_minute']
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']

        high_demean = high.values / np.nanmean(high.values, axis=0) 
        low_demean = low.values / np.nanmean(low.values, axis=0)
        volume_demean = volume.values / np.nanmean(volume.values, axis=0)
        price_range = high_demean - low_demean
        mid_price = (high_demean + low_demean) / 2.
        ans = - np.nanmean(volume_demean[1:] * price_range[1:] * (mid_price[1:] - mid_price[:-1]), axis=0)

        ans = pd.Series(ans, index=volume.columns)
        ans[~np.isfinite(ans)] = np.nan        
        return ans

                
                        
                                                                        
    def  reform(self, temp_result):
        A = temp_result.rolling(60,1).std()
        return -A

