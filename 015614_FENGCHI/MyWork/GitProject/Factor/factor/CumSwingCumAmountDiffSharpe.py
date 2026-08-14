# -*- coding: utf-8 -*-
'''
* 因子名称：CumSwingCumAmountDiffSharpe_13h
* 描述：(归一化累计振幅 - 归一化累计成交额)的Sharpe
* 因子逻辑：因子越大，成交额的增长速度逐渐大于振幅增长的速度，放量时股价波动较小的股票有超额收益
* 因子参数：分钟数据的成交额、最高价、最低价
* 作者：何丰敬
* 日期：2019.10.14
* 函数修改日期:尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
'''
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
class CumSwingCumAmountDiffSharpe(BaseFactor):
    
    factor_type = 'FIX'
    s_amt_min = 'FactorData.Basic_factor.amt_minute'
    s_high_min = 'FactorData.Basic_factor.high_minute'
    s_low_min = 'FactorData.Basic_factor.low_minute'
    depend_data = [s_amt_min, s_high_min, s_low_min]

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        amt_min = database.depend_data[self.s_amt_min]
        high_min = database.depend_data[self.s_high_min]
        low_min = database.depend_data[self.s_low_min]
        
        return self.minute(amt_min, high_min, low_min)
    
    def minute(self, MinuteTurnover, MinuteHigh, MinuteLow):
        high = MinuteHigh.rolling(len(MinuteHigh), min_periods=1).max()
        low = MinuteLow.rolling(len(MinuteLow), min_periods=1).min()
        ran = high - low
        ran = ran / ran.iloc[-1]  # 归一化累计振幅
        amount = MinuteTurnover.cumsum()
        amount = amount / amount.iloc[-1]  # 归一化累计成交额
        diff = ran - amount
        return diff.mean() / diff.std()
