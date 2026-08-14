from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class WRMean5d_13h(BaseFactor):

    """
    *因子名：WRMean5d_13h
    *因子功能描述：当日截至13:00，当日均价（分钟vwap的均值）的威廉指标-过去5天威廉指标的均值。
    当日威廉指标=(2*当日均价-昨收至今最高价-昨收至今最低价)/(昨收至今最高价-昨收至今最低价)
    该值越大，说明当日市场较强，前几日市场较弱，股票存在日内动量和隔日反转效应，则存在超额收益。
    *因子参数：[MinuteTurnover]: 分钟成交额
               [MinuteVolume]: 分钟成交量
               [MinuteHigh]: 分钟最高价
               [MinuteLow]: 分钟最低价
               [close]: 收盘价
               [high]: 最高价
               [low]: 最低价

    *作者：周璇
    *因子创建日期：2019.8.20
    *函数修改日期：尚未修改
    *修改人：尚未修改
    *修改原因：尚未修改
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.volume_adj_minute", "FactorData.Basic_factor.high_adj_minute", "FactorData.Basic_factor.low_adj_minute", "FactorData.Basic_factor.high_badj", "FactorData.Basic_factor.low_badj", "FactorData.Basic_factor.close_badj"]
    lag = 5
    minute_lag = 1

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        a = database.depend_data['FactorData.Basic_factor.amt_minute']
        v = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        h = database.depend_data['FactorData.Basic_factor.high_adj_minute']
        l = database.depend_data['FactorData.Basic_factor.low_adj_minute']
        cc = database.depend_data['FactorData.Basic_factor.close_badj']
        hh = database.depend_data['FactorData.Basic_factor.high_badj']
        ll = database.depend_data['FactorData.Basic_factor.low_badj']
        date_list = sorted(np.unique(a.index.strftime('%Y-%m-%d')))
        date = date_list[-1]
        pre_date = date_list[-2].replace('-','')
        amt = a.loc[date]
        volume = v.loc[date]
        vwap = amt/volume
        high_min = h.loc[date].max(axis=0)
        low_min = l.loc[date].min(axis=0)
        high_min[cc.loc[pre_date]>high_min] = cc.loc[pre_date]
        low_min[cc.loc[pre_date]<low_min] = cc.loc[pre_date]
        WRMean5d = (2*np.ones(high_min.shape)*vwap.mean(axis=0)-high_min-low_min)/(high_min-low_min)
        WR = (2*np.ones(cc.loc[:pre_date].shape)*cc.loc[:pre_date]-hh.loc[:pre_date]-ll.loc[:pre_date])/(hh.loc[:pre_date]-ll.loc[:pre_date])
        return WRMean5d-WR.rolling(window=5,min_periods=4).mean().iloc[-1]