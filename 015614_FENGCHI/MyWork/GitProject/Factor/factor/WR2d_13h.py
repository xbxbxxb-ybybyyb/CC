from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class WR2d_13h(BaseFactor):

    """
    *因子名：WR2d_13h
    *因子功能描述：13:00收盘价的威廉指标-前一日最高价、最低价和收盘价计算的威廉指标。当日收盘价采用近10min收盘价的均值。
    当日收益具有动量效应、前一日具有反转效应，将二者结合，构建复合威廉指标，当日上升势头强，前一日涨势有限的股票，后市有继续上涨的动力。
    *因子参数：[MinuteClose]: 分钟收盘价
               [MinuteHigh]: 分钟最高价
               [MinuteLow]: 分钟最低价
               [close]: 收盘价
               [high]: 最高价
               [low]: 最低价

    *作者：周璇
    *因子创建日期：2019.7.19
    *函数修改日期：尚未修改
    *修改人：尚未修改
    *修改原因：尚未修改
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.close_adj_minute", "FactorData.Basic_factor.high_adj_minute", "FactorData.Basic_factor.low_adj_minute", "FactorData.Basic_factor.high_badj", "FactorData.Basic_factor.low_badj", "FactorData.Basic_factor.close_badj"]
    lag = 1
    minute_lag = 1

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        c = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        h = database.depend_data['FactorData.Basic_factor.high_adj_minute']
        l = database.depend_data['FactorData.Basic_factor.low_adj_minute']
        cc = database.depend_data['FactorData.Basic_factor.close_badj']
        hh = database.depend_data['FactorData.Basic_factor.high_badj']
        ll = database.depend_data['FactorData.Basic_factor.low_badj']
        date_list = sorted(np.unique(c.index.strftime('%Y-%m-%d')))
        date = date_list[-1]
        pre_date = date_list[-2].replace('-','')
        close_min = c.loc[date]
        high_min = h.loc[date].max(axis=0)
        low_min = l.loc[date].min(axis=0)
        high_min[cc.loc[pre_date]>high_min] = cc.loc[pre_date]
        low_min[cc.loc[pre_date]<low_min] = cc.loc[pre_date]
        WR = (2*np.ones(high_min.shape)*close_min.iloc[-10:].mean(axis=0)-high_min-low_min)/(high_min-low_min)
        wr_pre = (2*np.ones(high_min.shape)*cc.loc[pre_date]-hh.loc[pre_date]-ll.loc[pre_date])/(hh.loc[pre_date]-ll.loc[pre_date])
        return WR-wr_pre
