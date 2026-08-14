# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

from xfactor.FixUtil import minute_data_transform

"""

    *因子名 : MinVVCorrRankStd
    *因子功能描述 : 最后30分钟量价相关性rank值*日间vwap与量的相关性的rank的5日波动率
    *因子参数 : MinuteVolume-成交量 MinuteClose-分钟收盘价
    *作者 : 薛晓伟
    *因子创建日期 : 2019.02.25

"""

class MinVVCorrRankStd(BaseFactor):
    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute"
        , "FactorData.Basic_factor.vwap","FactorData.Basic_factor.volume"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 5
    minute_lag = 0
    # 定义播放后对所有结果做后处理的rolling窗口长度，默认reform_window=1，可不设置
    reform_window = 5
    # fix_times = ["1500"]

    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):

        data_minute = {"FactorData.Basic_factor.close_minute":database.depend_data['FactorData.Basic_factor.close_minute']
                        ,"FactorData.Basic_factor.volume_minute":database.depend_data['FactorData.Basic_factor.volume_minute']}
        minute_data_transform(data_minute,operation=['drop','merge'])

        close_minute = data_minute["FactorData.Basic_factor.close_minute"]
        volume_minute = data_minute["FactorData.Basic_factor.volume_minute"]

        vwap = database.depend_data["FactorData.Basic_factor.vwap"]
        volume = database.depend_data["FactorData.Basic_factor.volume"]

        vol_close_corr = Util.array_coef(close_minute[-30:],volume_minute[-30:])
        vol_close_corr_rank = vol_close_corr.rank(pct=True)

        # vwap_vol_corr = vwap.rolling(window=self.lag,min_periods=1).corr(volume)
        vwap_vol_corr = Util.rolling_corr(vwap, volume, self.lag)
        vwap_vol_corr_rank = vwap_vol_corr.rank(pct=True,axis=1)

        return pd.Series(data=vol_close_corr_rank.values*vwap_vol_corr_rank.iloc[-1].values,index=close_minute.columns)

    def reform(self,temp_result):
        return -temp_result.rolling(window=self.reform_window,min_periods=1).std()

    # def definition(self,MinuteVolume,MinuteClose,vwap_adj,volume):
    #     vwap_vol_corr = vwap_adj.rolling(window=5,min_periods=1).corr(other=volume)
    #     vwap_vol_corr_rank = vwap_vol_corr.rank(pct=True,axis=1)
    #     min_result = self.minute_help(self.cal,'MinVVCorrRankStdHelp',MinuteVolume,MinuteClose)
    #
    #     result = vwap_vol_corr_rank*min_result
    #     result_std = -1*result.rolling(window=5,min_periods=1).std()
    #
    #     return result_std
    #
    #
    # def cal(self,MinuteVolume,MinuteClose):
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteVolume.index.strftime(fmt))
    #     df = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list],columns=MinuteVolume.columns)
    #
    #     for date in date_list:
    #         close = MinuteClose.loc[date]
    #         volume = MinuteVolume.loc[date]
    #
    #
    #         vol_close_corr = close[-30:].corrwith(other=volume[-30:])
    #         vol_close_corr_rank = vol_close_corr.rank(pct=True)
    #
    #         df.loc[date] = vol_close_corr_rank
    #
    #     return df