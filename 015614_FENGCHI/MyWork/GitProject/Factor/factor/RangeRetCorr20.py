# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd


class RangeRetCorr20(BaseFactor):
    
    '''
    * 因子名：RangeRetCorr20
    * 逻辑：该因子计算了振幅与收益率的相关性，两者双双到达顶点时往往意味着行情结束，是一种反转效应
    * 因子参数：分钟数据的高开低收
    * 作者：陈卓
    * 日期：2019.1.2
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close", "FactorData.Basic_factor.high", "FactorData.Basic_factor.low", 
    "FactorData.Basic_factor.amt", "FactorData.Basic_factor.adjfactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 21

    def calc_single(self, database):
        n = 20
        nd = n

        close = database.depend_data['FactorData.Basic_factor.close']
        high = database.depend_data['FactorData.Basic_factor.high']
        low = database.depend_data['FactorData.Basic_factor.low']
        amt = database.depend_data['FactorData.Basic_factor.amt']
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']

        cp_valid = close* adjfactor
        hp_valid = high * adjfactor
        lp_valid = low * adjfactor
        prange = hp_valid - lp_valid
        # cp_diff = cp_valid / cp_valid.shift(1) - 1
        cp_diff = cp_valid / cp_valid.shift(1)
        cp_diff = pd.DataFrame(cp_diff.values - 1, index=cp_valid.index, columns=cp_valid.columns)
        # dp = prange.rolling(nd).corr(cp_diff)
        dp = Util.array_coef(prange.iloc[-nd:,:], cp_diff.iloc[-nd:,:])
        # alpha = -1.* dp
        return -dp
