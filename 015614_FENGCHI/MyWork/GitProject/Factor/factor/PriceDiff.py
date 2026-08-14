# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '/data/group/800020/AlphaFramework/FactorManagement/')
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd

class PriceDiff(BaseFactor):
    """

    *因子名 : PriceDiff
    *因子功能描述 : 
        民生证券研报因子的改进，近两日日内收益率加权均值与横截面股票的相对排名，反转因子
        
    *因子参数 : close_adj-调整最高价，vwap_adj-调整开盘价，is_valid-是否合法
    *作者 : 肖倩
    *因子创建日期 : 2019.04.02
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改


    """


    # def definition(self, close_adj, vwap_adj, is_valid,n=20):
    #     diff = close_adj - vwap_adj
    #     price_max_rank = close_adj.rolling(window=n).max().rank(pct=True, axis=1)
    #     price_max_rank_emm = self.rolling_ewm(price_max_rank, 2)
    #     alpha = self.rolling_ewm(diff / price_max_rank_emm,n)
    #     alpha[~np.isfinite(alpha)] = np.nan
    #     alpha[is_valid == 0] = np.nan

    #     return -1*alpha

    factor_type = "DAY"

    s_close = 'FactorData.Basic_factor.close'
    s_vwap = 'FactorData.Basic_factor.vwap'
    s_adjfactor = 'FactorData.Basic_factor.adjfactor'
    depend_data = [s_close , s_vwap, s_adjfactor]

    n = 20

    lag = n

    def rolling_ewm(self, df, n):
        seq = [2 * i / (n * (n + 1)) for i in range(1, n + 1)]
        weight = np.array(seq)
        return df.rolling(window = n).apply(lambda x: np.sum(x * weight))

    def calc_single(self, database):
        close= database.depend_data[self.s_close]
        vwap = database.depend_data[self.s_vwap]
        adjfactor = database.depend_data[self.s_adjfactor]
        vwap_adj = vwap * adjfactor
        close_adj = close * adjfactor
        diff = (close_adj - vwap_adj)

        price_max_rank = close_adj.rolling(self.n,min_periods=1).max().rank(pct=True, axis=1)
        
        price_max_rank_emm = self.rolling_ewm(price_max_rank, 2)
        res = self.rolling_ewm((-diff / price_max_rank_emm),self.n)

        res[~np.isfinite(res)] = np.nan

        return res.iloc[-1]

    # def reform(self, temp_result):
    #     temp = self.rolling_ewm(temp_result, self.n)
    #     temp[~np.isfinite(temp)] = np.nan
    #     return temp_result

