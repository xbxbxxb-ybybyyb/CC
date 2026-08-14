# -*- coding: utf-8 -*-
'''
* 因子名称：SharpeDuringAmountDrop
* 描述：计算当日开盘至13:00期间成交额由最高点下降到低点过程中，分钟收益率的Sharpe值
* 因子逻辑：以分钟收益率的Sharpe值衡量大规模换手之后股票确立的走势
* 因子参数：分钟数据的成交额、成交量
* 作者：何丰敬
* 日期：2019.9.11
* 函数修改日期:尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
'''
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

class SharpeDuringAmountDrop(BaseFactor):
    
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.amt_minute','FactorData.Basic_factor.volume_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 0
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])

        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']

        r = (MinuteTurnover / MinuteVolume).pct_change()
        amount = MinuteTurnover.rolling(10).mean()  # 计算滚动10分钟平均成交额
        amount_max = amount.max()
        amount_max_rolling = amount.rolling(len(amount), min_periods=1).max()
        amount_down = amount[amount_max_rolling == amount_max]  # 筛选出出成交额最高点之后的部分
        amount_min = amount_down.min()
        amount_min_rolling = amount_down.rolling(len(amount_down), min_periods=1).min()
        r_down = r[amount_min_rolling > amount_min]  # # 筛选出成交额从最高点下降到低点的部分
        return r_down.mean() / r_down.std()

    # def definition(self, MinuteTurnover, MinuteVolume):
    #     factor = self.minute_help(self.minute, 'MinuteValidRetHelp', MinuteTurnover, MinuteVolume)
    #     return factor
    
    
    # def minute(self, MinuteTurnover, MinuteVolume):
    #     r = (MinuteTurnover / MinuteVolume).pct_change()
    #     amount = MinuteTurnover.rolling(10).mean()  # 计算滚动10分钟平均成交额
    #     amount_max = amount.max()
    #     amount_max_rolling = amount.rolling(len(amount), min_periods=1).max()
    #     amount_down = amount[amount_max_rolling == amount_max]  # 筛选出出成交额最高点之后的部分
    #     amount_min = amount_down.min()
    #     amount_min_rolling = amount_down.rolling(len(amount_down), min_periods=1).min()
    #     r_down = r[amount_min_rolling > amount_min]  # # 筛选出成交额从最高点下降到低点的部分
    #     return r_down.mean() / r_down.std()