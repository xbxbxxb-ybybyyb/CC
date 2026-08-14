from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class CorrDelVolumePriceSharpe5d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.volume_minute"]
    lag = 0
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        volume_change = abs(volume.diff(1))
        CorrDelVolumePrice= Util.array_coef(volume_change,close)

        return -CorrDelVolumePrice
    
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window,1).mean()/temp_result.rolling(self.reform_window,1).std()
    
    