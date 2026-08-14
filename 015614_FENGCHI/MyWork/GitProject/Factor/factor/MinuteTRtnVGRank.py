from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class MinuteTRtnVGRank(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute",
                   "FactorData.Basic_factor.volume_minute",
                "FactorData.Basic_factor.is_valid", ]

    lag = 0
    
    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        valid = pd.DataFrame(is_valid.values==1, index=is_valid.index, columns=is_valid.columns)

        re = close_minute.values/close_minute.shift(1).values - 1
        re = pd.DataFrame(re, index = close_minute.index, columns=close_minute.columns)
        
        minute_volume_growth_rate = volume_minute.values/volume_minute.shift(1).values - 1
        minute_volume_growth_rate[np.isinf(minute_volume_growth_rate)] = np.nan
        minute_volume_growth_rate = pd.DataFrame(minute_volume_growth_rate, index = close_minute.index, columns=close_minute.columns)
        
        condi1 = pd.DataFrame(re.values > (re.mean()+2*re.std()).values, index = re.index, columns=re.columns)
        condi2 = pd.DataFrame(re.values < (re.mean()-2*re.std()).values, index = re.index, columns=re.columns)
        minute_volume_high_rtn = minute_volume_growth_rate[-60:][condi1]
        minute_volume_low_rtn = minute_volume_growth_rate[-60:][condi2]
        result = minute_volume_low_rtn.mean().rank() - minute_volume_high_rtn.mean().rank()
        return result[valid.iloc[-1]]

