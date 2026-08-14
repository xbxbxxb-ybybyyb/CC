# -*- coding: utf-8 -*-
"""
    * 因子名：MinPrePriceRate
    * 因子功能描述：计算五分钟最低价到当日最高价的最高变化率，表示当日最大可获利收益，反转因子，值越大，越容易反转
    * 因子参数：  MinuteHigh, MinuteLow
    * 作者：肖倩
    * 因子创建日期： 2019.8.11
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
"""

import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

class MinPrePriceRate(BaseFactor):
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.close_minute','FactorData.Basic_factor.high_minute','FactorData.Basic_factor.low_minute']    
    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 1
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series
    # reform_window = 5

    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteHigh.index.strftime(fmt)))
        pre_date = date_list[-2]
        compute_date = date_list[-1]
        high_df = MinuteHigh.loc[pre_date:compute_date].rolling(5,1).mean()
        low_df = MinuteLow.loc[compute_date].rolling(5,1).mean()
        close_df = MinuteClose.loc[compute_date]
        ret = (high_df.max()-close_df)/(high_df.max()-low_df.min())
        
        return ret.max().rank()+ret.min().rank()

    # def definition(self, MinuteHigh, MinuteLow,MinuteClose):
    #     factor = self.minute_help(self.minute, 'MinPrePriceRateHelp', MinuteHigh, MinuteLow,MinuteClose)
    #     return factor
    # def minute(self, MinuteHigh, MinuteLow,MinuteClose):

    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteHigh.index.strftime(fmt)))
    #     pre_date = date_list[-2]
    #     compute_date = date_list[-1]
    #     high_df = MinuteHigh.loc[pre_date:compute_date].rolling(5,1).mean()
    #     low_df = MinuteLow.loc[compute_date].rolling(5,1).mean()
    #     close_df = MinuteClose.loc[compute_date]
    #     ret = (high_df.max()-close_df)/(high_df.max()-low_df.min())
    #     return ret.max().rank()+ret.min().rank()
