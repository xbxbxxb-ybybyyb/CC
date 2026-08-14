from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class hfCPVCorrHDbias_13h(BaseFactor):

    '''
    * 因子名：hfCPVCorrHDbias_13h
    * 描述：昨日下午到今日上午30min的close与volume相关性，减去5日均值除以标准差
    * 逻辑：昨日午盘今日上午盘的量价齐飞，热度反转
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
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        c = database.depend_data['FactorData.Basic_factor.close_adj_minute'].iloc[-240:]
        v = database.depend_data['FactorData.Basic_factor.volume_adj_minute'].iloc[-240:]
        return Util.array_coef(c, v)

    def reform(self, temp):
        bs =  (temp.astype(float) - np.ones(temp.shape) * temp.rolling(5).mean()) / temp.rolling(5).std()
        df = -bs.rolling(5,1).mean()
        return df