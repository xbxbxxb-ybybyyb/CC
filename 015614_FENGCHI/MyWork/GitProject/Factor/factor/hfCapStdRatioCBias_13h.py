from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class hfCapStdRatioCBias_13h(BaseFactor):

    '''
    * 因子名：hfCapStdRatioCBias_13h
    * 描述：今日截止1点的主买主卖时段容量的波动率对比，5日bias
    * 逻辑：多空某一方之波动越大，后续反转概率较大
    * 因子参数：分钟数据的高开低收
    * 作者：陈卓
    * 日期：2019.6.23
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.volume_adj_minute", "FactorData.Basic_factor.close_adj_minute", "FactorData.Basic_factor.low_adj_minute", "FactorData.Basic_factor.high_adj_minute", "FactorData.Basic_factor.open_adj_minute"]
    lag = 0
    minute_lag = 1
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        o = database.depend_data['FactorData.Basic_factor.open_adj_minute'].iloc[-240:]
        h = database.depend_data['FactorData.Basic_factor.high_adj_minute'].iloc[-240:]
        l = database.depend_data['FactorData.Basic_factor.low_adj_minute'].iloc[-240:]
        c = database.depend_data['FactorData.Basic_factor.close_adj_minute'].iloc[-240:]
        a = database.depend_data['FactorData.Basic_factor.amt_minute'].iloc[-240:]
        v = database.depend_data['FactorData.Basic_factor.volume_adj_minute'].iloc[-240:]
        vwap = a / v
        rs_flag = (vwap.diff(1) > np.zeros(vwap.shape))
        high_cap = h * v
        low_cap = l * v
        skew = (high_cap[rs_flag] / (np.ones(vwap.shape)*high_cap[rs_flag].mean().values)).std() / (low_cap[~rs_flag] / (np.ones(vwap.shape)*low_cap[~rs_flag].mean().values)).std()
        skew[~np.isfinite(skew)] = np.nan
        return skew
 
    def reform(self, temp):
        bs =  (temp.astype(float) - temp.rolling(5,1).mean()) / temp.rolling(5,1).std()
        df = -bs.rolling(5,1).mean()
        return df