# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

"""
    * 因子名：MinVwapHLRateBeta
    * 因子功能描述：计算5分钟最大成交额与成交量的vwap与最高价跟最低价价格比率之间的beta，取一段时间窗口因子值delta
    * 因子参数：  MinuteClose,MinuteHigh, MinuteLow
    * 作者： 肖倩
    * 因子创建日期： 2019.7.29
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
"""
class MinVwapHLRateBetaDelta(BaseFactor):
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.high_minute','FactorData.Basic_factor.low_minute','FactorData.Basic_factor.amt_minute','FactorData.Basic_factor.volume_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 0
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series
    reform_window = 11
    
    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])

        amt_df = database.depend_data['FactorData.Basic_factor.amt_minute']
        volume_df = database.depend_data['FactorData.Basic_factor.volume_minute']
        high_df = database.depend_data['FactorData.Basic_factor.high_minute']
        low_df = database.depend_data['FactorData.Basic_factor.low_minute']
        n=5
        vwap_df = (amt_df.rolling(n,n).max() / volume_df.rolling(n,n).max()).rank(axis=0)
        hl_df = (high_df.rolling(n,n).max() / low_df.rolling(n,n).min()).rank(axis=0)
        corr_vwap_hl_df = Util.array_coef(vwap_df, hl_df)
        res = corr_vwap_hl_df*vwap_df.std(axis=0)/hl_df.std(axis=0)
        return res
    
    def reform(self, temp_result):
        return -1*self.delta(temp_result,self.reform_window - 1)

    # def definition(self, MinuteHigh, MinuteLow, MinuteTurnover, MinuteVolume):
    #     res = self.minute_help(self.minute, 'MinVwapHLBeta_14h', MinuteHigh, MinuteLow, MinuteTurnover, MinuteVolume)
    #     return -1*self.delta(res,10)

    # def minute(self, MinuteHigh, MinuteLow, MinuteTurnover, MinuteVolume):
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteHigh.index.strftime(fmt))
    #     compute_date = date_list[-1]
    #     amt_df = MinuteTurnover.loc[compute_date]
    #     volume_df = MinuteVolume.loc[compute_date]
    #     high_df = MinuteHigh.loc[compute_date]
    #     low_df = MinuteLow.loc[compute_date]
    #     n=5
    #     vwap_df = (amt_df.rolling(n,n).max() / volume_df.rolling(n,n).max()).rank(axis=0)
    #     hl_df = (high_df.rolling(n,n).max() / low_df.rolling(n,n).min()).rank(axis=0)
    #     res = vwap_df.corrwith(hl_df)*vwap_df.std(axis=0)/hl_df.std(axis=0)
    #     return res

    def delta(self,factor,window):
        res = factor-factor.shift(window)
        return res