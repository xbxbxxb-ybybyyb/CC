# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteVolumeHHISharpe(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.volume_minute"]
    lag = 0
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteVolume.index.strftime(fmt))

        date = date_list[-1]
        volume = MinuteVolume.loc[date]
        volume = volume.resample('10T').sum().iloc[-15:]
        volume_sum_squared = np.square(volume.sum(axis=0))
        volume_squared = np.square(volume)
        temp = pd.DataFrame(volume_squared.values/volume_sum_squared.values,index=volume.index,columns=volume.columns)
        hhi = temp.sum(axis=0)

        if len(hhi.dropna()) != 0:
            res = hhi
        else:
            res = pd.Series(0.0,index=volume.columns)

        return res

    def reform(self, temp_result):
        return temp_result.rolling(window=self.reform_window,min_periods=1).mean()/temp_result.rolling(window=self.reform_window,min_periods=1).std()
