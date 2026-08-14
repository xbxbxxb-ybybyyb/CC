from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteRetLastHrSkew(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))

        date = date_list[-1]
        close = MinuteClose.loc[date].values
        vol_last = (close[-1] - close[-60]) / close[-60]
        if np.sum(~np.isnan(vol_last))==0:
            vol_last = np.array([0.0]*MinuteClose.shape[1])

        return pd.Series(vol_last,index=MinuteClose.columns)

    def reform(self, temp_result):
        result = -temp_result.rolling(10,1).skew()
        return result.rolling(10,1).mean()/result.rolling(10,1).std()