from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteTPVDeltaCorr(BaseFactor):
    """

    *因子名 : MinuteTPVDeltaCorr
    *因子功能描述 : 尾盘15分钟分钟成交量与分钟close价格增量的相关性
    *因子参数 : MinuteClose-分钟末端价格，MinuteVolume-分钟成交量
    *作者 : 沈天琦(shentq)
    *因子创建日期 : 2019.04.28
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改


    """
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute"]
    lag = 0
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        c = database.depend_data['FactorData.Basic_factor.close_minute']
        v = database.depend_data['FactorData.Basic_factor.volume_minute']
        
        vv = (v - v.shift(1)).iloc[-15:]
        cc = (c - c.shift(1)).iloc[-15:]
        return -Util.array_coef(vv, cc)

    def reform(self, temp):
        return temp.rolling(window=self.reform_window, min_periods=1).mean()