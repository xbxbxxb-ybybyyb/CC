# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

from xfactor.FixUtil import minute_data_transform
"""

*因子名 : Last30MinutesLongShortRatio
*因子功能描述 : 收盘前30分钟vwap与close比值的平均，衡量收盘赢利比例

*作者 : wulb
*因子创建日期 : 2019.1.2

"""

class Last30MinsVwapCloseRatio5d(BaseFactor):

    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.close_minute",
                   "FactorData.Basic_factor.amt_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 0
    minute_lag = 0
    # 定义播放后对所有结果做后处理的rolling窗口长度，默认reform_window=1，可不设置
    reform_window = 10
    # fix_times = ["1500"]
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):
        minute_data_transform(database.depend_data,operation=["drop","merge"])

        close_minute = database.depend_data["FactorData.Basic_factor.close_minute"]
        volume_minute = database.depend_data["FactorData.Basic_factor.volume_minute"]
        turnover_minute = database.depend_data["FactorData.Basic_factor.amt_minute"]

        vwap_adj = turnover_minute / volume_minute
        vwap_adj = vwap_adj.fillna(method='ffill')
        df_ratio = vwap_adj / close_minute

        last_30_ratios = df_ratio[-30:].mean()
        last_30_ratios[~np.isfinite(last_30_ratios)] = np.nan

        return last_30_ratios

    def reform(self, temp_result):
        return temp_result.rolling(window=self.reform_window,min_periods=1).mean()

    # def definition(self, MinuteClose, MinuteTurnover, MinuteVolume, is_valid):
    #     minute_factor_df = self.minute_help(self.minute, 'Last30MinsVwapCloseRatio5dHelp', MinuteClose, MinuteTurnover, MinuteVolume)
    #     minute_factor_df = minute_factor_df.rolling(window=5,min_periods=1).mean()
    #     minute_factor_df[is_valid == 0] = np.nan
    #
    #     return minute_factor_df
    #
    # def minute(self, MinuteClose, MinuteTurnover, MinuteVolume):
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteClose.index.strftime(fmt))
    #     minute_factor = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list],columns=MinuteClose.columns)
    #
    #     for date in date_list:
    #         close_adj = MinuteClose.loc[date]
    #         turnover = MinuteTurnover.loc[date]
    #         volume = MinuteVolume.loc[date]
    #
    #         vwap_adj = turnover / volume
    #         vwap_adj = vwap_adj.fillna(method='ffill')
    #
    #         ratio = vwap_adj / close_adj
    #
    #         day_factor = ratio[-30:].mean()
    #
    #         day_factor[~np.isfinite(day_factor)] = np.nan
    #         minute_factor.loc[date] = day_factor
    #
    #     #print(minute_factor)
    #     return minute_factor
        
