from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class Volatility_13h(BaseFactor):
    """
    * 因子名：Volatility_13h
    * 因子功能描述：下午一点前15分钟价格的波动率.波动率大则看跌.
    * 因子参数： MinuteVolume
    * 作者：姚逸凡
    * 因子创建日期： 2019.6.24
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.open_minute"]
    lag = 0
    minute_lag = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        v = database.depend_data['FactorData.Basic_factor.open_minute']
        return -((v / v.shift(1) - np.ones(v.shape)).iloc[-15:]).std()