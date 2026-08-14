from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteCloseTurnRev(BaseFactor):
    
    '''
    * 因子名：MinuteCloseTurnRev
    * 逻辑：该因子是一个分钟因子，主要在于衡量尾盘价量趋势反转
    * 因子参数：分钟数据收盘价成交额，自由流通市值
    * 日期：2019.05.09
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.free_float_shares", "FactorData.Basic_factor.close", "FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.close_minute"]
    lag = 0

    def calc_single(self, database):
        c = database.depend_data['FactorData.Basic_factor.close'].iloc[-1]
        ffs = database.depend_data['FactorData.Basic_factor.free_float_shares'].iloc[-1]
        ffc = ffs * c
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        a = database.depend_data['FactorData.Basic_factor.amt_minute'].loc[:, c.index]
        c = database.depend_data['FactorData.Basic_factor.close_minute'].loc[:, c.index]
        liq = a.iloc[-15:].sum() / ffc
        c_ma = c.iloc[-5:].mean() / c.iloc[-30:].mean()
        liq_rank = liq.rank(ascending=False, pct=True)
        c_ma_rank = c_ma.rank(ascending=False, pct=True)
        return liq_rank + c_ma_rank