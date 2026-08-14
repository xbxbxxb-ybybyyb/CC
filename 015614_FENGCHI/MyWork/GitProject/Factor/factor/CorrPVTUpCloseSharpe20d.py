from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

class CorrPVTUpCloseSharpe20d(BaseFactor):


    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.volume_minute"]

    lag = 0
    reform_window = 20

    def calc_single(self,database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        re = close/close.shift(1)
        re_volume = np.where(volume.values>volume.shift(1).values,re.values*volume.values,np.nan)
        re_volume = pd.DataFrame(re_volume,index=close.index,columns=close.columns)
        Corr = Util.array_coef(close,re_volume)

        return -Corr
    
    def reform(self, temp_result):
        A = temp_result.rolling(self.reform_window, min_periods=1).mean()/temp_result.rolling(self.reform_window, min_periods=1).std()
        return A