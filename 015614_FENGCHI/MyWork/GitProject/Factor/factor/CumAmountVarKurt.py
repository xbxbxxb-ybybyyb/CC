# -*- coding: utf-8 -*-
'''
* 因子名称：CumAmountVarKurt_13h
* 描述：成交额累计方差偏离时间线性增长的峰度
* 因子逻辑：因子越大，成交活跃度变化出现非线性增长的频率越高，可能成为市场热点
* 因子参数：分钟数据的成交额
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
class CumAmountVarKurt(BaseFactor):
    
    factor_type = "FIX"
    s_amt_min = 'FactorData.Basic_factor.amt_minute'
    depend_data = [s_amt_min]

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        amt_min = database.depend_data[self.s_amt_min]
        return self.minute(amt_min)
    
    
    def minute(self, MinuteTurnover):
        amount_mean = MinuteTurnover.mean()
        var = ((MinuteTurnover - amount_mean) ** 2).cumsum()
        var = var / var.iloc[-1].replace(0, np.nan)  # 归一化累计方差
        linear = pd.DataFrame(np.ones(var.shape), index=var.index, columns=var.columns)
        linear = linear.cumsum()
        linear = linear / linear.iloc[-1]  # 从0线性增长到1
        diff = var - linear
        return diff.kurt()