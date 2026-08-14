from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class WilliamsPriceVolCorrMultiple_13h(BaseFactor):
    """
    * 因子名：WilliamsPriceVolCorrMultiple_13h
    * 因子功能描述：计算量价相关性 与 williams indicator的乘积。
    * 因子参数： MinuteOpen,MinuteHigh, MinuteLow,MinuteVolume。
    * 作者：姚逸凡
    * 因子创建日期： 2019.6.24
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.open_minute", "FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute", "FactorData.Basic_factor.volume_minute"]
    lag = 0
    minute_lag = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        o = database.depend_data['FactorData.Basic_factor.open_minute']
        h = database.depend_data['FactorData.Basic_factor.high_minute']
        l = database.depend_data['FactorData.Basic_factor.low_minute']
        v = database.depend_data['FactorData.Basic_factor.volume_minute']
        # date_list = sorted(np.unique(c.index.strftime('%Y-%m-%d')))
        corr = Util.array_coef(o, v)
        indicator = -(h.max() - o.iloc[-1]) / (h.max() - l.min())
        mult = corr * indicator
        return mult
