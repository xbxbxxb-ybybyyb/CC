from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class hfCPVCorrHDmean_13h(BaseFactor):

    '''
    * 因子名：hfCPVCorrHDmean_13h
    * 描述：昨日下午到今日上午30min的close与volume相关性，5日均值取负值
    * 逻辑：昨日午盘今日上午盘的量价齐飞，热度反转
    * 因子参数：分钟数据的高开低收
    * 作者：陈卓
    * 日期：2019.6.23
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.close_adj_minute", "FactorData.Basic_factor.volume_adj_minute"]
    lag = 0
    minute_lag = 1
    reform_window = 5
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        c = database.depend_data['FactorData.Basic_factor.close_adj_minute'].iloc[-240:]
        v = database.depend_data['FactorData.Basic_factor.volume_adj_minute'].iloc[-240:]
        return Util.array_coef(c, v)

    def reform(self, temp):
        df = -temp.rolling(5,1).mean()
        return df