# -*- coding: utf-8 -*-
'''
* 因子名称：SharpeDuringStdDrop
* 描述：计算当日开盘至13:00期间股票分钟收益率的滚动10分钟波动率由最高点下降到低点过程中，分钟收益率的Sharpe值
* 因子逻辑：波动率高的时刻是多空双方对抗相持的阶段，在这之后若股票收益率Sharpe值较高，则说明多头在对抗中逐渐占据了优势
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

class SharpeDuringStdDrop(BaseFactor):
    
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

        minute_data_transform(database.depend_data, operation=["drop","merge"])

        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']

        r = (MinuteTurnover / MinuteVolume).pct_change()
        std = r.rolling(10).std()  # 计算滚动10分钟波动率
        std_max = std.max()
        std_max_rolling = std.rolling(len(std), min_periods=1).max()
        std_down = std[std_max_rolling == std_max]  # 筛选出出现波动率最高点之后的部分
        std_min = std_down.min()
        std_min_rolling = std_down.rolling(len(std_down), min_periods=1).min()
        r_down = r[std_min_rolling > std_min]  # 筛选出波动率从最高点下降到低点的部分
        return r_down.mean() / r_down.std()

    # def definition(self, MinuteTurnover, MinuteVolume):
    #     factor = self.minute_help(self.minute, 'MinuteValidRetHelp', MinuteTurnover, MinuteVolume)
    #     return factor
    
    
    # def minute(self, MinuteTurnover, MinuteVolume):
    #     r = (MinuteTurnover / MinuteVolume).pct_change()
    #     std = r.rolling(10).std()  # 计算滚动10分钟波动率
    #     std_max = std.max()
    #     std_max_rolling = std.rolling(len(std), min_periods=1).max()
    #     std_down = std[std_max_rolling == std_max]  # 筛选出出现波动率最高点之后的部分
    #     std_min = std_down.min()
    #     std_min_rolling = std_down.rolling(len(std_down), min_periods=1).min()
    #     r_down = r[std_min_rolling > std_min]  # 筛选出波动率从最高点下降到低点的部分
    #     return r_down.mean() / r_down.std()