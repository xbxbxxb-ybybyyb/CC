# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class HighFreqVolumeMACmp(BaseFactor):   
     # 因子频率，。默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume_adj_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    minute_lag = 1
    # fix_times=["1300"]

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_adj_minute']  
        factor = self.minute_help(MinuteVolume)
        return factor


    def minute_help(self, MinuteVolume):

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        compute_date = date_list[-1]
        pre_date = date_list[-2]
                
        volume = MinuteVolume.loc[compute_date]
        volume_pre = MinuteVolume.loc[pre_date]        
        volume_pre_ = volume_pre.iloc[:len(volume)]
        volume_pre_ = pd.DataFrame(data=volume_pre_.values,index=volume.index,columns=volume.columns)

        volume_ma = volume.rolling(window=5).mean()
        volume_pre_ma = volume_pre_.rolling(window=5).mean()

        volume_ma_r = volume_pre_ma/volume_ma
        volume_ma_r_mean = volume_ma_r.mean()

        return volume_ma_r_mean