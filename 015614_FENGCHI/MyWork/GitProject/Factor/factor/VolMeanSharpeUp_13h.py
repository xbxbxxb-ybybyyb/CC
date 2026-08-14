from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class VolMeanSharpeUp_13h(BaseFactor):

    """
    *因子名：VolMeanSharpeUp_13h
    *因子功能描述：当日截至13:00，分钟收盘价大于前5min均价时的成交量夏普率,成交量为5min平均成交量。
    该值越大，说明上涨时成交量越大且稳定，后市存在上涨动量。
    *因子参数：[MinuteClose]: 分钟收盘价
               [MinuteVolume]: 分钟成交量

    *作者：周璇
    *因子创建日期：2019.8.14
    *函数修改日期：尚未修改
    *修改人：尚未修改
    *修改原因：尚未修改
    """

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute"]
    lag = 0
    minute_lag = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        c = database.depend_data['FactorData.Basic_factor.close_minute']
        v = database.depend_data['FactorData.Basic_factor.volume_minute']
        c_mean = c.rolling(window=5,min_periods=4).mean()
        v_mean = v.rolling(window=5,min_periods=4).mean()

        VolSharpeUp = v_mean[c>c_mean].mean(axis=0)/v_mean[c>c_mean].std(axis=0)
        return -VolSharpeUp
