# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

from xfactor.FixUtil import minute_data_transform
'''
    * 因子名：MinuteCloseTurnPlus
    * 逻辑：该因子是一个分钟因子，衡量尾盘价量趋势反转
    * 因子参数：分钟数据收盘价成交额，日频收盘价
    * 作者：xust
    * 日期：2019.04.18

'''

class MinuteCloseTurnPlus(BaseFactor):
    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.close_badj","FactorData.Basic_factor.is_valid"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 10
    minute_lag = 10
    # 定义播放后对所有结果做后处理的rolling窗口长度，默认reform_window=1，可不设置
    # reform_window = 5
    # fix_times = ["1500"]
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):

        data_minute = {"FactorData.Basic_factor.close_minute":database.depend_data['FactorData.Basic_factor.close_minute']
                        ,"FactorData.Basic_factor.amt_minute":database.depend_data['FactorData.Basic_factor.amt_minute']}
        minute_data_transform(data_minute,operation=['drop','merge'])

        close_minute = data_minute['FactorData.Basic_factor.close_minute']
        turnover_minute = data_minute['FactorData.Basic_factor.amt_minute']
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']

        fmt = '%Y-%m-%d'
        date_list = np.unique(close_minute.index.strftime(fmt))
        t_ma = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list], columns=close_minute.columns)
        c_ma = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list], columns=close_minute.columns)
        t_ma_norm = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list], columns=close_minute.columns)
        c_ma_norm = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list], columns=close_minute.columns)
        df_alpha = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list], columns=close_minute.columns)

        for date in date_list:
            t = turnover_minute.loc[date]
            c = close_minute.loc[date]
            t_ma.loc[date] = t.iloc[-5:].mean() / t.iloc[-30:].mean()
            c_ma.loc[date] = c.iloc[-5:].mean() / c.iloc[-30:].mean()
        
            t_ma_norm.loc[date] = t_ma.loc[date].subtract(t_ma.loc[date].min(), axis=0).divide(t_ma.loc[date].max()-t_ma.loc[date].min(), axis=0)
            c_ma_norm.loc[date] = c_ma.loc[date].subtract(c_ma.loc[date].min(), axis=0).divide(c_ma.loc[date].max()-c_ma.loc[date].min(), axis=0)
        
            df_alpha.loc[date] = pd.Series(-1 * (t_ma_norm.loc[date] * c_ma_norm.loc[date]).values, index=t_ma_norm.loc[date].index)
        
        is_valid_1 = pd.DataFrame(is_valid.values==1,index=is_valid.index,columns=is_valid.columns)
        close_ma = close_adj[is_valid_1].rolling(window=5, min_periods=1).mean() / close_adj[is_valid_1].rolling(window=10, min_periods=10).mean()
        close_ma_norm = close_ma.subtract(close_ma.min(axis=1), axis=0).divide(close_ma.max(axis=1)-close_ma.min(axis=1), axis=0)
        
        return (df_alpha * close_ma_norm).rolling(window=5, min_periods=1).mean().iloc[-1]


    # def definition(self, MinuteClose, MinuteTurnover, Minute_Status, close_adj, is_valid_raw, n=5):
    #     close_ma = close_adj[is_valid_raw==1].rolling(window=5, min_periods=1).mean() / close_adj[is_valid_raw==1].rolling(window=10, min_periods=10).mean()
    #     close_ma_norm = close_ma.subtract(close_ma.min(axis=1), axis=0).divide(close_ma.max(axis=1)-close_ma.min(axis=1), axis=0)
    #     alpha = self.minute_help(self.minute, 'MinuteCloseTurnHelp', MinuteClose, MinuteTurnover)
    #     alpha = alpha[Minute_Status==0] * close_ma_norm
    #     alpha = alpha.rolling(window=n, min_periods=1).mean()
    #     return alpha
    #
    # def minute(self, MinuteClose, MinuteTurnover):
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteClose.index.strftime(fmt))
    #     t_ma = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list], columns=MinuteClose.columns)
    #     c_ma = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list], columns=MinuteClose.columns)
    #     for date in date_list:
    #         t = MinuteTurnover.loc[date]
    #         c = MinuteClose.loc[date]
    #         t_ma.loc[date] = t.iloc[-5:].mean() / t.iloc[-30:].mean()
    #         c_ma.loc[date] = c.iloc[-5:].mean() / c.iloc[-30:].mean()
    #     t_ma_norm = t_ma.subtract(t_ma.min(axis=1), axis=0).divide(t_ma.max(axis=1)-t_ma.min(axis=1), axis=0)
    #     c_ma_norm = c_ma.subtract(c_ma.min(axis=1), axis=0).divide(c_ma.max(axis=1)-c_ma.min(axis=1), axis=0)
    #     alpha = -1 * t_ma_norm * c_ma_norm
    #     return alpha