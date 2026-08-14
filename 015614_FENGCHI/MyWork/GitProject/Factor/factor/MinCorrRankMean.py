# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

from xfactor.FixUtil import minute_data_transform
"""

*因子名 : MinCorrRankMean
*因子功能描述 : 量占比的rank值*量价相关性*vwap与量的相关性的rank的5日均值
*作者 : 薛晓伟
*因子创建日期 : 2019.02.18


"""
class MinCorrRankMean(BaseFactor):
    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.close_minute","FactorData.Basic_factor.adjfactor",
                   "FactorData.Basic_factor.vwap","FactorData.Basic_factor.volume"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 5
    minute_lag = 5
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
        volume_day = database.depend_data["FactorData.Basic_factor.volume"]
        vwap_adj = database.depend_data["FactorData.Basic_factor.vwap"] * database.depend_data["FactorData.Basic_factor.adjfactor"]

        fmt = '%Y-%m-%d'
        date_list = np.unique(volume_minute.index.strftime(fmt))
        df_result = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list],columns=volume_minute.columns)

        for d in date_list:
            close = close_minute.loc[d]
            volume = volume_minute.loc[d]
    
            volume_last = volume[-10:].sum()/volume[-30:].sum()
            volume_last_rank = volume_last.rank(pct=True)
    
    
            vol_close_corr = Util.array_coef(close[-10:],volume[-10:])
            vol_close_corr_rank = vol_close_corr.rank(pct=True)
            vol_close = vol_close_corr_rank*volume_last_rank

            df_result.loc[d] = vol_close


        vwap_vol_corr = Util.rolling_corr(vwap_adj,volume_day,5)
        vwap_vol_corr_rank = vwap_vol_corr.rank(pct=True,axis=1)
        result = vwap_vol_corr_rank*df_result
        result_mean = result.rolling(window=5,min_periods=1).mean()
    
        return pd.DataFrame(-1 * result_mean.values, index=result_mean.index, columns=result_mean.columns).iloc[-1]







    # def definition(self,MinuteVolume,MinuteClose,vwap_adj,volume):
    #
    #     vwap_vol_corr = vwap_adj.rolling(window=5,min_periods=1).corr(other=volume)
    #     vwap_vol_corr_rank = vwap_vol_corr.rank(pct=True,axis=1)
    #     min_result = self.minute_help(self.cal,'MinCorrRankMeanHelp',MinuteVolume,MinuteClose)
    #     result = vwap_vol_corr_rank*min_result
    #     result_mean = -1*result.rolling(window=5,min_periods=1).mean()
    #
    #     return result_mean
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
    #         volume_last = volume[-10:].sum()/volume[-30:].sum()
    #         volume_last_rank = volume_last.rank(pct=True)
    #
    #
    #         vol_close_corr = close[-10:].corrwith(other=volume[-10:])
    #         vol_close_corr_rank = vol_close_corr.rank(pct=True)
    #         vol_close = vol_close_corr_rank*volume_last_rank
    #
    #         df.loc[date] = vol_close
    #
    #     return df