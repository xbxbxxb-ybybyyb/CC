from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteliqSwingStd5(BaseFactor):
    """

    *因子名 : MinuteliqSwingStd5
    *因子功能描述 : Illiq代表单位资金推动股价变动的幅度。查找流动性好的时候Amt加权振幅。取5日std

    *因子参数 : MinuteTurnover, MinuteClose,MinuteHigh,MinuteLow, is_valid_raw, Minute_Status
    *作者 : 刘正
    *因子创建日期 : 2019.05.15
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改

    """
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute", "FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        h = database.depend_data['FactorData.Basic_factor.high_minute']
        l = database.depend_data['FactorData.Basic_factor.low_minute']
        c = database.depend_data['FactorData.Basic_factor.close_minute']
        a = database.depend_data['FactorData.Basic_factor.amt_minute']
        a5 = a.groupby(pd.Grouper(freq='5min')).sum().dropna(how='all')
        c5 = c.groupby(pd.Grouper(freq='5min')).last().dropna(how='all')
        h5 = h.groupby(pd.Grouper(freq='5min')).max().dropna(how='all')
        l5 = l.groupby(pd.Grouper(freq='5min')).min().dropna(how='all')
        swing = (h5 - l5) / c5.shift(1)
        r = c5 / c5.shift(1) - np.ones(c5.shape)
        illiq = r.abs() / a5
        z = (illiq - np.repeat(illiq.mean().values.reshape(1, -1), illiq.shape[0], axis=0)) / np.repeat(illiq.std().values.reshape(1, -1), illiq.shape[0], axis=0)

        return (swing * a5[z<2*np.ones(z.shape)]).sum() / a5.sum()


    def reform(self, temp):
        return -temp.rolling(window=self.reform_window, min_periods=1).std()