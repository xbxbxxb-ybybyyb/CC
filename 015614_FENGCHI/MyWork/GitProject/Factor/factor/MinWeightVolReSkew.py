# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class MinWeightVolReSkew(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    reform_window = 5
    fix_times=["1500"]
    def calc_single(self,database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        
        min_result = self.minute_help(volume,close)
        # result = -min_result.iloc[-5:,:].skew()

        return min_result
    def reform(self, temp_result):
        return -temp_result.rolling(window=5,min_periods=1).skew()

    def minute_help(self,MinuteVolume,MinuteClose): 
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteVolume.index.strftime(fmt))
        # df = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list],columns=MinuteVolume.columns)
        weight = np.array([0.5+0.5/240*(i+1) for i in range(240)])
        weight = weight.reshape(240,1)
        one = np.ones((1,MinuteVolume.shape[1]))[0]
        weight = pd.DataFrame(weight*one,columns=MinuteVolume.columns)
        
        for date in date_list:
            close = MinuteClose.loc[date]
            volume = MinuteVolume.loc[date]
            weight.index = close.index
            volume = weight*volume
            vol_mean = volume.mean()
            vol_ratio = volume/volume.mean()
            re = close.pct_change(1)
            vol_re = vol_ratio*re
            vol_re = vol_re[-120:]
            
            df = vol_re.sum()
        return df