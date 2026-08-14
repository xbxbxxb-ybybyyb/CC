from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteCloseTurn(BaseFactor):
    
    '''
    * 因子名：MinuteCloseTurn
    * 逻辑：该因子是一个分钟因子，衡量尾盘价量趋势反转
    * 因子参数：分钟数据收盘价成交额
    * 日期：2019.04.18
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        a = database.depend_data['FactorData.Basic_factor.amt_minute']
        c = database.depend_data['FactorData.Basic_factor.close_minute']

        a_ma = a.iloc[-5:].mean() / a.iloc[-30:].mean()
        c_ma = c.iloc[-5:].mean() / c.iloc[-30:].mean()
        a_ma_norm = (a_ma - a_ma.min()) / (a_ma.max() - a_ma.min())
        c_ma_norm = (c_ma - c_ma.min()) / (c_ma.max() - c_ma.min())
        return -1 * a_ma_norm * c_ma_norm

    def reform(self, temp):
        return temp.rolling(window=self.reform_window, min_periods=1).mean()