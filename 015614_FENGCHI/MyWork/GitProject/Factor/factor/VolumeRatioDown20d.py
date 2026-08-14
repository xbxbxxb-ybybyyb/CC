from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class VolumeRatioDown20d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.pct_chg",
                   "FactorData.Basic_factor.volume_minute",
                "FactorData.Basic_factor.is_valid", ]

    lag = 0
    reform_window = 20
    
    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        pct_chg= database.depend_data['FactorData.Basic_factor.pct_chg'].iloc[-1]
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        valid = pd.DataFrame(is_valid.values==1, index=is_valid.index, columns=is_valid.columns)
                
        factor = volume_minute[:30].sum(axis=0)/volume_minute[120:150].sum(axis=0)
        result = -factor[pct_chg<0]
        return result[valid.iloc[-1]]

    def reform(self, temp_result):
        return temp_result.rolling(window=self.reform_window ,min_periods=1).mean()
