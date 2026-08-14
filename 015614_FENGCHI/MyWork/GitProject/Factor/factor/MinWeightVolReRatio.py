from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinWeightVolReRatio(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.volume_minute"]
    lag = 0
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))

        weight = np.array([0.5+0.5/240*(i+1) for i in range(240)])
        weight = weight.reshape(240,1)
        one = np.ones((1,MinuteVolume.shape[1]))[0]
        weight = weight*one

        date = date_list[-1]
        volume = MinuteVolume.loc[date].values
        close = MinuteClose.loc[date].values          
        
        volume = weight*volume
        vol_mean = np.nanmean(volume,axis=0)
        vol_ratio = volume/vol_mean
        re = close/MinuteClose.loc[date].shift(1).values-1
        vol_re = vol_ratio*re
        res = np.nansum(vol_re[-120:],axis=0)

        return pd.Series(res,index=MinuteClose.columns)

    def reform(self, temp_result):
        mean_ = temp_result.rolling(window=self.reform_window,min_periods=1).mean()
        std_ = temp_result.rolling(window=self.reform_window,min_periods=1).std()
        return -mean_/std_