from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class CorrMaxRePriceRank(BaseFactor):  # 派生一个因子类
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.high_minute', 'FactorData.Basic_factor.low_minute',
                    'FactorData.Basic_factor.close_minute','FactorData.Basic_factor.open_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    minute_lag=0
    # fix_times = ["1300"]
    # reform_window = 5


    """
    *因子名：CorrMaxRePriceRank_13h
    *因子功能描述：当日截至13:00，每分钟最大涨幅or最大跌幅与价格的秩相关性。
    当分钟close>open,计算(close-low+high-open)/open，当close<open,计算(high-close+open-low)/open
    该因子值越小，说明价格低时涨幅较大，价格高时跌幅较小，后市上涨动力存在。
    *因子参数：[MinuteClose]: 分钟收盘价
               [MinuteOpen]: 分钟开盘价
               [MinuteHigh]: 分钟最高价
               [MinuteLow]: 分钟最低价
               [MinuteVolume]: 分钟成交量

    *作者：周璇
    *因子创建日期：2019.7.10
    *函数修改日期：尚未修改
    *修改人：尚未修改
    *修改原因：尚未修改
    """


    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']

        c = MinuteClose
        o = MinuteOpen
        h = MinuteHigh
        l = MinuteLow
        r = (c-l+h-o)/o
        flag = pd.DataFrame(c.values<o.values, index=c.index, columns=c.columns)
        r[flag] = (h-c+o-l)/o
        CorrMaxRePriceRank = Util.array_coef(r.rank(), c.rank())
        return -CorrMaxRePriceRank