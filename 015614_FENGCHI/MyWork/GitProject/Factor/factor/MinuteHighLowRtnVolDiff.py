# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

from xfactor.FixUtil import minute_data_transform
"""
*因子名 : MinuteHighLowRtnVolDiff
*因子描述 : 当日较低收益率成交量与较高收益率成交量之差与全天平均成交量的比值再取10日平均
*因子逻辑：较低行情成交量代表未来买盘力量，反之为卖盘力量，因子反映未来上涨预期。
*作者 : 沈天琦
*因子创建日期 : 2020.02.19
"""
class MinuteHighLowRtnVolDiff(BaseFactor):
    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 10
    minute_lag = 0
    # 定义播放后对所有结果做后处理的rolling窗口长度，默认reform_window=1，可不设置
    # reform_window = 5
    # fix_times=["1500"]
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):

        data_minute = {"FactorData.Basic_factor.close_minute":database.depend_data['FactorData.Basic_factor.close_minute']
                        ,"FactorData.Basic_factor.volume_minute":database.depend_data['FactorData.Basic_factor.volume_minute']}
        minute_data_transform(data_minute,operation=['drop','merge'])

        close_minute = data_minute["FactorData.Basic_factor.close_minute"]
        volume_minute = data_minute["FactorData.Basic_factor.volume_minute"]
        
        rtn_minute = (close_minute - close_minute.shift(1)) / close_minute.shift(1)

        rtn_minute_mean = rtn_minute.mean(axis=0)
        rtn_minute_std = rtn_minute.std(axis=0)

        df_is_rtn_high = pd.DataFrame(rtn_minute.values > (rtn_minute_mean.values+rtn_minute_std.values) , index=rtn_minute.index, columns=rtn_minute.columns)
        df_is_rtn_low = pd.DataFrame(rtn_minute.values < (rtn_minute_mean.values-rtn_minute_std.values), index=rtn_minute.index, columns=rtn_minute.columns)

        df_high_volume = volume_minute[df_is_rtn_high]
        df_low_volume = volume_minute[df_is_rtn_low]
        
        result = (df_low_volume.mean(axis=0) - df_high_volume.mean(axis=0)) / volume_minute.mean(axis=0)
        

        return result

    
    def reform(self,temp_result):
        return temp_result.rolling(window=self.lag, min_periods=1).mean()