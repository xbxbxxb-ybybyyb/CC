from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class hfCapSkewRatio_13h(BaseFactor):

    '''
    * 因子名：hfCapSkewRatio_13h
    * 描述：今日上午的主买主卖时段容量的偏度对比
    * 逻辑：多空某一方之偏度右偏严重，后续反转概率较大
    * 因子参数：分钟数据的高开低收
    * 作者：陈卓
    * 日期：2019.6.23
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.low_minute", "FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.open_minute"]
    lag = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        o = database.depend_data['FactorData.Basic_factor.open_minute']
        h = database.depend_data['FactorData.Basic_factor.high_minute']
        l = database.depend_data['FactorData.Basic_factor.low_minute']
        c = database.depend_data['FactorData.Basic_factor.close_minute']
        a = database.depend_data['FactorData.Basic_factor.amt_minute']
        v = database.depend_data['FactorData.Basic_factor.volume_minute']
        vwap = a / v
        rs_flag = (vwap.diff(1) > np.zeros(vwap.shape))
        high_cap = h * v
        low_cap = l * v
        skew = high_cap[rs_flag].skew() / low_cap[~rs_flag].skew()
        skew[~np.isfinite(skew)] = np.nan
        return -skew