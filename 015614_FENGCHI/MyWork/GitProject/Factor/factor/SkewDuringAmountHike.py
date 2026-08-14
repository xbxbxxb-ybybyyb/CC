# -*- coding: utf-8 -*-
'''
* 因子名称： SkewDuringAmountHike
* 描述： 成交额上升时间段的超额收益偏度
* 因子逻辑： 成交额上升时尾部风险依然较小的股票具有超额收益
* 因子参数： 分钟数据的成交额、成交量
* 作者： 何丰敬
* 日期： 2019.10.25
* 函数修改日期: 尚未修改
* 修改人： 尚未修改
* 修改原因： 尚未修改
'''


import numpy as np
import pandas as pd

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform


class SkewDuringAmountHike(BaseFactor):
    
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.volume_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 0
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']

        r = (MinuteTurnover.cumsum() / MinuteVolume.cumsum()).pct_change()
        r = r.sub(r.mean(axis=1), axis=0)  # 超额收益
        amount_rolling_max = MinuteTurnover.rolling(len(MinuteTurnover), min_periods=1).max()
        amount_up = MinuteTurnover[amount_rolling_max < MinuteTurnover.max()]
        amount_rolling_min = amount_up.rolling(len(amount_up), min_periods=1).min()  # 筛选出成交额上升的时间段
        r_up = r[amount_rolling_min == amount_up.min()]
        return r.skew() - r_up.skew()  # 9:30-11:30超额收益偏度 - 成交额上升时间段的超额收益偏度

    # def definition(self, MinuteTurnover, MinuteVolume):
    #     factor = self.minute_help(self.minute, 'MinuteValidRetHelp', MinuteTurnover, MinuteVolume)
    #     return factor
    
    
    # def minute(self, MinuteTurnover, MinuteVolume):
    #     r = (MinuteTurnover.cumsum() / MinuteVolume.cumsum()).pct_change()
    #     r = r.sub(r.mean(axis=1), axis=0)  # 超额收益
    #     amount_rolling_max = MinuteTurnover.rolling(len(MinuteTurnover), min_periods=1).max()
    #     amount_up = MinuteTurnover[amount_rolling_max < MinuteTurnover.max()]
    #     amount_rolling_min = amount_up.rolling(len(amount_up), min_periods=1).min()  # 筛选出成交额上升的时间段
    #     r_up = r[amount_rolling_min == amount_up.min()]
    #     return r.skew() - r_up.skew()  # 9:30-11:30超额收益偏度 - 成交额上升时间段的超额收益偏度