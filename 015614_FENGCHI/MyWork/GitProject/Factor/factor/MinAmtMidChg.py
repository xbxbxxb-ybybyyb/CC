# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinAmtMidChg(BaseFactor):
    
    '''
    * 因子名：MinAmtMidChg
    * 逻辑：该因子是一个分钟因子，主要在于衡量全天分钟级的成交量加权的价格变化，并做平滑，是一种长期反转效应
    * 因子参数：分钟数据的高开低收
    * 作者：陈卓
    * 日期：2019.1.15
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.volume_minute", \
    "FactorData.Basic_factor.low_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 20
        
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']

        fmt = '%Y-%m-%d' 
        date = np.unique(MinuteHigh.index.strftime(fmt))[0] 
        df_ratio = pd.DataFrame(index=[pd.Timestamp(date)], columns=MinuteHigh.columns) 
         
        min_high = MinuteHigh.loc[date]
        min_low = MinuteLow.loc[date]
        min_mid = (min_high+min_low) / 2
        min_volume = MinuteVolume.loc[date]
        min_volume_relavtive = pd.DataFrame(min_volume.values/min_volume.mean().values,index=min_volume.index,columns=min_volume.columns)
        min_mid_diff = pd.DataFrame(min_mid/min_mid.shift(1).values-1,index=min_mid.index,columns=min_mid.columns)
        dn = (min_volume_relavtive * min_mid_diff).sum()
        dn = -dn
        return dn

    def reform(self, dailyf):
        alpha = dailyf.rolling(window=self.reform_window, min_periods=int(self.reform_window/2)).mean()
        return alpha                
