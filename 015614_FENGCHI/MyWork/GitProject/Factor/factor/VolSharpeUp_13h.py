from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class VolSharpeUp_13h(BaseFactor):

    """
    *因子名：VolSharpeUp_13h
    *因子功能描述：当日截至13:00，记当日收益率均值为r_mean,收益率>r_mean时的成交量夏普率。
    该值越大，说明上涨时成交量越大且稳定，后市存在上涨动量。
    *因子参数：[MinuteClose]: 分钟收盘价
               [MinuteVolume]: 分钟成交量

    *作者：周璇
    *因子创建日期：2019.8.13
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
        r = c/c.shift(1)-np.ones(c.shape)
        VolSharpeUp = v[r>r.mean().values*np.ones(r.shape)].mean()/v[r>r.mean().values*np.ones(r.shape)].std()
        return -VolSharpeUp