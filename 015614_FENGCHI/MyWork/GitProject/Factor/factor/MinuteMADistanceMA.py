# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

from xfactor.FixUtil import minute_data_transform

"""

*因子名 : MinuteMADistanceMA
*因子功能描述 : 计算尾盘价格与均线的趋同程度,反映趋势稳健程度，该因子值均值作为因子值
*函数返回值 : MinuteMADistanceMA
*作者 : 孙海平
*因子创建日期 : 2019.4.16

"""
class MinuteMADistanceMA(BaseFactor):
    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 0
    minute_lag = 0
    # 定义播放后对所有结果做后处理的rolling窗口长度，默认reform_window=1，可不设置
    reform_window = 5
    # fix_times = ["1500"]
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):

        minute_data_transform(database.depend_data,operation=["drop","merge"])

        close_minute = database.depend_data["FactorData.Basic_factor.close_minute"]
        close_mean = close_minute.rolling(window=10).mean()

        length = 30
        close_dis = (abs(close_minute - close_mean) / close_mean)[-length:].sum()
        ret = close_minute.iloc[-1].values / close_minute.iloc[-length].values - 1

        ans = (ret / abs(ret)) / close_dis.values

        return pd.Series(ans, index=close_minute.columns)

    def reform(self, temp_result):
        return -temp_result.rolling(window=self.reform_window, min_periods=1).mean()

    # def definition(self,MinuteClose):
    #     df_skew1 = -self.minute_help(self.minute,'MinuteMADistanceMAHelp',MinuteClose)
    #     n = 5
    #     df_skew1 = df_skew1.rolling(window = n,min_periods=1).mean()
    #     return df_skew1
    #
    # def minute(self,MinuteClose):
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteClose.index.strftime(fmt))
    #     df_skew = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list],columns=MinuteClose.columns)
    #     for date in date_list:
    #         Close = MinuteClose.loc[date]
    #         n = 10
    #         close_mean = Close.rolling(window=n).mean()
    #
    #         length = 30
    #         close_dis = (abs(Close - close_mean)/close_mean)[-length:].sum()
    #         ret = Close.iloc[-1]/Close.iloc[-length]-1
    #         factor1 = (ret/abs(ret))*1/close_dis
    #         df_skew.loc[date]=factor1
    #
    #     return df_skew


