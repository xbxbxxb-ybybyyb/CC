from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform


class MinCorrVolumeRetUp5d(BaseFactor):


    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.volume_minute"]

    lag = 0
    reform_window = 5

    def calc_single(self,database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        re = (close/close.shift(1)).values-1
        re_big = pd.DataFrame(np.where(re>0,re,np.nan),index=close.index,columns=close.columns)
        volume_big = pd.DataFrame(np.where(re>0,volume.values,np.nan),index=close.index,columns=close.columns)
        corr = Util.array_coef(re_big,volume_big)
        return -corr
    
    def reform(self, temp_result):
        A = temp_result.rolling(self.reform_window, min_periods=1).mean()
        return A