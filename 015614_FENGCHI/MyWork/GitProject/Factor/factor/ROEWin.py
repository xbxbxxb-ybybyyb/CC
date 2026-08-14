# -*- coding: utf-8 -*-

"""

*因子名 : ROEWin
*因子功能描述 : 计算ROE 量价因子, 挑选ROE较好但量价超跌股票
*因子参数 : trun-成交量 eps_ttm-每股收益 roe_ttm-净资产收益率 free_float_cap-自由流通市值 amt-成交额 is_valid-是否合法
*函数返回值 : ROE 量价因子
*作者 : 孙海平
*因子创建日期 : 2018.12.18
*函数修改日期 : 尚未修改
*修改人 ：尚未修改
*修改原因 :  尚未修改
*版本 : 1.0
*历史版本 : 无

"""
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time


class ROEWin(BaseFactor):  # 派生一个因子类
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    s_Wind = 'FactorData.WIND_AShareFinancialIndicator'
    # s_ps_ttm = 'FactorData.Basic_factor.ps_ttm'
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.free_float_shares","FactorData.Basic_factor.close",
                    "FactorData.Basic_factor.volume", "FactorData.Basic_factor.amt",s_Wind,
                    "FactorData.Basic_factor.is_valid"]
                   
                
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    financial_lag = 200
    lag = 10
    reform_window = 10


        
    def calc_single(self, database):

        volume = database.depend_data['FactorData.Basic_factor.volume']
        amt = database.depend_data['FactorData.Basic_factor.amt']
        free_float_shares = database.depend_data['FactorData.Basic_factor.free_float_shares']
        close = database.depend_data['FactorData.Basic_factor.close']
        Wind = database.depend_data[self.s_Wind]
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']

        eps = Wind['S_FA_EPS_BASIC']
        eps = eps.unstack().fillna(method='ffill')
        eps = eps.reindex(amt.columns, axis = 1)
        eps = eps.iloc[-1]
        roe_ttm_orig = Wind['S_FA_ROE_AVG']
        roe_ttm_orig = roe_ttm_orig.unstack().fillna(method='ffill')
        roe_ttm = roe_ttm_orig.reindex(amt.columns, axis = 1)
        roe_ttm = roe_ttm.iloc[-1]

        # print(roe_ttm)


        n = 10
        # cap = free_float_cap
        cap = free_float_shares * close
        vwap = amt/volume
        turn = volume

        turn_rate = amt/cap
        turn_rate_rank = turn_rate.iloc[-1,:].rank(pct=True,)

        vwap_max = vwap.max()
        vwap_min = vwap.min()
        vwap_adj = (vwap.iloc[-1,:] - vwap_min)/(vwap_max - vwap_min)

        turn_max = turn.max()
        turn_min = turn.min()
        turn_adj = (turn.iloc[-1,:] - turn_min)/(turn_max - turn_min)

        turn_adj_rank = turn_adj.rank(pct=True,)
        vwap_adj_rank = vwap_adj.rank(pct=True,)

        # turn_rate = amt/cap
        roe_rank = roe_ttm.rank(pct=True,)
        # turn_rate_rank = turn_rate.rank(pct=True,axis=1)
        # cap_rank = cap.rank(pct=True,axis=1)
        eps_ttm_rank = eps.rank(pct=True,)
        # print(turn_adj_rank)
        # print(vwap_adj_rank)
        # print(roe_rank)
        # print(eps_ttm_rank)


        alpha = (1 + roe_rank)*(1 + eps_ttm_rank)/(1 + (turn_adj_rank*vwap_adj_rank))/(1 + turn_rate_rank)
        
        # alpha_nd = alpha.rolling(window=n).mean()   
        # alpha_nd = 1/alpha_nd
        # print('done')

        return alpha

    def  reform(self, temp_result):
        A = temp_result.rolling(self.reform_window).mean()
        return A
