from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class WR_13h(BaseFactor):

    """
    *因子名：WR_13h
    *因子功能描述：13:00收盘价的威廉指标，((收盘价-昨日至今最低价)-(昨日至今最高价-收盘价))/(昨日至今最高价-昨日至今最低价)。
    衡量当前时点的价格位置，该值越大，说明当前价格位置较高，存在继续上涨的动量。
    *因子参数：[MinuteClose]: 分钟收盘价
               [MinuteHigh]: 分钟最高价
               [MinuteLow]: 分钟最低价
               [high]: 最高价
               [low]: 最低价

    *作者：周璇
    *因子创建日期：2019.7.2
    *函数修改日期：尚未修改
    *修改人：尚未修改
    *修改原因：尚未修改
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.close_adj_minute", "FactorData.Basic_factor.high_adj_minute", "FactorData.Basic_factor.low_adj_minute", "FactorData.Basic_factor.high_badj", "FactorData.Basic_factor.low_badj"]
    lag = 1
    minute_lag = 1

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        c = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        h = database.depend_data['FactorData.Basic_factor.high_adj_minute']
        l = database.depend_data['FactorData.Basic_factor.low_adj_minute']
        hh = database.depend_data['FactorData.Basic_factor.high_badj']
        ll = database.depend_data['FactorData.Basic_factor.low_badj']
        date_list = sorted(np.unique(c.index.strftime('%Y-%m-%d')))
        date = date_list[-1]
        pre_date = date_list[-2].replace('-', '')
        close = c.loc[date]
        high_today = h.loc[date].max(axis=0)
        low_today = l.loc[date].min(axis=0)
        h = hh.loc[pre_date]
        l = ll.loc[pre_date]
        h[high_today>h] = high_today
        l[low_today<l] = low_today
        WR = (2*np.ones(l.shape)*close.iloc[-1]-h-l)/(h-l)
        return WR
