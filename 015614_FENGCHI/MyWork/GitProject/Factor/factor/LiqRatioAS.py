# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import time


class LiqRatioAS(BaseFactor):
    
    '''
    * 因子名：LiqRatioAS
    * 逻辑：该因子为成交量相对于自由流通股本占比，反映股票的流动性和关注度
    * 因子参数：成交额，自由流通市值，is_valid_raw
    * 作者：xust
    * 日期：2019.01.23
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.amt", "FactorData.Basic_factor.free_float_shares", "FactorData.Basic_factor.close"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 15
    reform_window = 15

    def calc_single(self, database):

        amt = database.depend_data['FactorData.Basic_factor.amt']
        free_float_shares = database.depend_data['FactorData.Basic_factor.free_float_shares']
        close = database.depend_data['FactorData.Basic_factor.close']

        amt_by_yuan = amt.iloc[-1,:] * 1000
        free_float_cap = free_float_shares.iloc[-1,:]*close.iloc[-1,:]*10000
        
        # turn = amt_by_yuan[is_valid_raw==1] / free_float_cap
        turn = amt_by_yuan / free_float_cap
        # alpha = turn.rolling(window=n, min_periods=int(n/2)).mean() / turn.rolling(window=n, min_periods=int(n/2)).std()
        # return alpha
        return turn

    def reform(self, temp_result):
        temp_result_mean = temp_result.rolling(self.reform_window,min_periods=self.reform_window//2).mean()
        temp_result_std = temp_result.rolling(self.reform_window,min_periods=self.reform_window//2).std()
        A = temp_result_mean / temp_result_std
        return A
        