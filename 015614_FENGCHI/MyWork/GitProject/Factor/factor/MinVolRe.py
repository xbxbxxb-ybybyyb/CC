# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd

class MinVolRe(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute"]
    reform_window = 30


    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        min_result = self.minute_help(volume, close)
        return min_result
    def weight(self,series):
        n = len(series)
        w = np.arange(1, (n + 1), 1) / n
        temp = (series * w).sum()
        return temp
    def reform(self, temp_result):
        factor_values =  temp_result.rolling(window=5, min_periods=1).skew()
        factor_values = factor_values.rank(axis=1, pct=True)
        return -factor_values.rolling(20,5).apply(self.weight)

    def minute_help(self, MinuteVolume, MinuteClose):
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteVolume.index.strftime(fmt))
        # df = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list],columns=MinuteVolume.columns)
        weight = np.array([0.5 + 0.5 / 240 * (i + 1) for i in range(240)])
        weight = weight.reshape(240, 1)
        one = np.ones((1, MinuteVolume.shape[1]))[0]
        weight = pd.DataFrame(weight * one, columns=MinuteVolume.columns)
        for date in date_list:
            close = MinuteClose.loc[date]
            volume = MinuteVolume.loc[date]
            weight.index = close.index
            volume = weight * volume
            vol_mean = volume.mean()
            vol_ratio = volume / volume.mean()
            re = close.pct_change(1)
            vol_re = vol_ratio * re
            vol_re = vol_re[-120:]
            df = vol_re.sum()
        return df