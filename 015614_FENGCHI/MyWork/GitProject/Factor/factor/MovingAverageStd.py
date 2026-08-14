# -*- coding: utf-8 -*-
"""
    * 因子名：MovingAverageStd_13h
    * 因子功能描述：计算前20分钟价格5min移动平均的标准差，该值越大则预测跌。
    * 因子参数： MinuteClose
    * 作者：姚逸凡
    * 因子创建日期： 2019.6.24
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
"""

import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

class MovingAverageStd(BaseFactor):

    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.close_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 0
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation=["drop","merge"])

        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        compute_date = date_list[-1]
        close = MinuteClose.loc[compute_date].iloc[-20:]   #13h using 20, 10h using 15
        ma = close.rolling(window=5, min_periods=1).mean()
        std = -ma.std()

        return std

    # def definition(self, MinuteClose):
    #     factor = self.minute_help(self.minute, 'MinuteValidRetHelp', MinuteClose)
    #     return factor

    # def minute(self, MinuteClose):

    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
    #     compute_date = date_list[-1]
    #     close = MinuteClose.loc[compute_date].iloc[-20:]   #13h using 20, 10h using 15
    #     ma = close.rolling(window=5, min_periods=1).mean()
    #     std = -ma.std()

    #     return std

