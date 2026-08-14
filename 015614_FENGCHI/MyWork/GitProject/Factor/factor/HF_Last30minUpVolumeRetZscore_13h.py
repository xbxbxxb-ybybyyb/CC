# coding: utf-8

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class HF_Last30minUpVolumeRetZscore_13h(BaseFactor):

    """
    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 1
    reform_window = 50

    """ 
    """
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        compute_date = date_list[-1]
        pre_date = date_list[-2]
        
        volume = MinuteVolume.loc[pre_date].iloc[-30:,:]
        
        tmp = MinuteClose.loc[pre_date].iloc[-30:,:]
        arr = tmp.values/tmp.shift(1).values-1

        ret = pd.DataFrame(arr,index=tmp.index,columns=tmp.columns)
        ret_sum = ret[volume>volume.shift()].sum()
        return -ret_sum
        


    def reform(self, factor):
        factor = self.zscore(factor,window=self.reform_window)
        factor.fillna(0.,inplace=True)
        return factor    

    def rolling_mean(self,factor,window):
        return factor.rolling(window=window,min_periods=1).mean()
    
    def rolling_std(self,factor,window):
        return factor.rolling(window=window,min_periods=1).std()
    
    def zscore(self,factor,window=5):
        return (factor-self.rolling_mean(factor,window=window)) / self.rolling_std(factor,window=window)

