from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteVolCVSkew10d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.volume_minute"]
    lag = 0
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))

        date = date_list[-1]
        close = MinuteClose.loc[date].values
        volume = MinuteVolume.loc[date].values
        
        close_1400 = close[-60]
        close_1500 =  close[-1]
        last_60_vol = volume[-60:]
        min_volcv_60m =np.nanstd(last_60_vol,axis=0,ddof=1)/np.nanmean(last_60_vol,axis=0)

        min_volcv_60m[np.isinf(min_volcv_60m)] = np.nan
        df_min_volcv_60m = (close_1500/close_1400 - 1.) * min_volcv_60m
        

        return pd.Series(df_min_volcv_60m,index=MinuteClose.columns)

    def reform(self, temp_result):
        result = -temp_result.rolling(self.reform_window,int(self.reform_window*0.5)).skew()
        return result.fillna(-1.)
