# -*- coding: utf-8 -*-
'''
* 因子名称：DrawdownSkew_13h
* 描述：当日开盘至13点股价回撤幅度的偏度,负向
* 因子逻辑：反转因子，大回撤出现频率高的股票后期反弹
* 因子参数：分钟数据的最高价、最低价
* 作者：何丰敬
* 日期：2019.8.6
* 函数修改日期:尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
'''
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
class DrawdownSkew(BaseFactor):

    factor_type = 'FIX'
    s_high_min = 'FactorData.Basic_factor.high_minute'
    s_low_min = 'FactorData.Basic_factor.low_minute'
    depend_data = [s_high_min, s_low_min]

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        high_min = database.depend_data[self.s_high_min]
        low_min = database.depend_data[self.s_low_min]
        return - self.minute(high_min, low_min)
    
    def minute(self, MinuteHigh, MinuteLow):
        roll_max = MinuteHigh.rolling(window=len(MinuteHigh), min_periods=1).max()
        a = (MinuteLow - roll_max) / roll_max
        return a.skew()