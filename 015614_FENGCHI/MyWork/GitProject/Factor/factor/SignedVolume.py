# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

"""
    * 因子名：SignedVolume
    * 因子功能描述：计算T-1日开盘到目前时刻的成交额的50日夏普。
    * 因子参数： MinuteTurnover
    * 作者：姚逸凡
    * 因子创建日期： 2019.6.24
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
"""

class SignedVolume(BaseFactor):

    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.amt_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 1
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series
    reform_window = 50

    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(database.depend_data['FactorData.Basic_factor.amt_minute'].index.strftime(fmt)))
        compute_date = date_list[-1]
        pre_date = date_list[-2]
        
        turnover = database.depend_data['FactorData.Basic_factor.amt_minute'].loc[compute_date]
        turnover_yesterday = database.depend_data['FactorData.Basic_factor.amt_minute'].loc[pre_date]

        result = turnover.sum() + turnover_yesterday.sum()

        return result

    def reform(self, temp_result):
        return temp_result.rolling(window = 50, min_periods=2).mean()/ temp_result.rolling(window = 50, min_periods=2).std()

    # def definition(self, MinuteTurnover):
    #     result = self.minute_help(self.minute, 'MinuteValidRetHelp', MinuteTurnover)
    #     result = result.rolling(window = 50, min_periods=2).mean()/ result.rolling(window = 50, min_periods=2).std()

    #     return result

    # def minute(self,  MinuteTurnover):

    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteTurnover.index.strftime(fmt)))
    #     compute_date = date_list[-1]
    #     pre_date = date_list[-2]
    #     turnover = MinuteTurnover.loc[compute_date]
    #     turnover_yesterday = MinuteTurnover.loc[pre_date]
    #     result = turnover.sum() + turnover_yesterday.sum()

        # return result