# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

from xfactor.FixUtil import minute_data_transform
"""

    *因子名 : MinuteVolVwapCorrCloseChg
    *因子功能描述 : 计算分钟级高频数据因子，尾盘半小时量价相关性与尾盘价格涨幅的乘积的5日均值
    *作者 : 薛晓伟
    *因子创建日期 : 2019.01.09

"""

class MinuteVolVwapCorrCloseChg(BaseFactor):
    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.volume_minute"
        , "FactorData.Basic_factor.close_minute"]
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

        turnover_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']

        vwap_values = turnover_minute.values / volume_minute.values
        vwap = pd.DataFrame(vwap_values,index=turnover_minute.index,columns=turnover_minute.columns)

        close_last = close_minute[-5:].mean()
        volume_half_hour = volume_minute[-30:]
        volume_ratio = sum(volume_half_hour.values) / sum(volume_minute.values)
        close_half_hour = close_minute[-35:-25].mean()
        vol_vwap_corr = Util.array_coef(vwap[-30:], volume_half_hour)

        close_chg_values = (close_last.values - close_half_hour.values) / close_half_hour.values
        ans = -1 * close_chg_values * volume_ratio * vol_vwap_corr.values

        return pd.Series(data=ans, index=vol_vwap_corr.index)

    def reform(self, temp_result):
        return temp_result.rolling(window=self.reform_window,min_periods=1).mean()

    # def definition(self,MinuteTurnover,MinuteVolume,MinuteClose):
    #
    #     up_var = self.minute_help(self.cal,'MinuteVolVwapCorrCloseChgHelp',MinuteTurnover,MinuteVolume,MinuteClose)
    #
    #     up_var_stat = up_var.rolling(window=5,min_periods=1).mean()
    #     return up_var_stat
    #
    # def cal(self,MinuteTurnover,MinuteVolume,MinuteClose):
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteTurnover.index.strftime(fmt))
    #     df = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list],columns=MinuteTurnover.columns)
    #
    #
    #     for date in date_list:
    #         close = MinuteClose.loc[date]
    #         volume = MinuteVolume.loc[date]
    #         turnover = MinuteTurnover.loc[date]
    #         vwap = turnover/volume
    #
    #         close_last = close[-5:].mean()
    #         volume_half_hour = volume[-30:]
    #         volume_ratio = volume_half_hour.sum()/volume.sum()
    #         close_half_hour = close[-35:-25].mean()
    #         vol_vwap_corr = vwap[-30:].corrwith(other=volume_half_hour)
    #
    #         close_chg = (close_last - close_half_hour)/close_half_hour
    #
    #         df.loc[date] = -1*close_chg*volume_ratio*vol_vwap_corr
    #
    #     return df