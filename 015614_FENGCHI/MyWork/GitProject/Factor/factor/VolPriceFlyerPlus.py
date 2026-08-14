# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

class VolPriceFlyerPlus(BaseFactor):
    
    '''
    * 因子名：VolPriceFlyerPlus
    * 逻辑：该因子为成交量相对于自由流通股本占比与收益率的相关性
    * 因子参数：成交额，自由流通市值，收盘价，is_valid_raw
    * 作者：xust
    * 日期：2019.01.23
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''

    factor_type = "DAY"
    s_close_badj = 'FactorData.Basic_factor.close_badj'
    s_turn = 'FactorData.Basic_factor.turn'
    depend_data = [s_close_badj, s_turn]

    n = 10
    lag = 2 * n -2
    reform_window = n
    def calc_single(self, database):
        n = self.n
        price = database.depend_data[self.s_close_badj]
        turn = database.depend_data[self.s_turn]
        turn_avg = turn.rolling(window=n, min_periods=n).mean()
        turn_std = turn.rolling(window=n, min_periods=n).std()
        turn_std = turn.std(axis = 0)
        turn_norm = (turn - turn_avg) / turn_std
        turn_norm = turn_norm.values
        turn_norm[np.isinf(turn_norm)] = np.nan
        turn_norm = pd.DataFrame(turn_norm, columns = turn_avg.columns, index = turn_avg.index)

        price_avg = price.rolling(window=n, min_periods=n).mean()
        price_std = price.rolling(window=n, min_periods=n).std()
        price_norm = (price - price_avg) / price_std
        price_norm = price_norm.values
        price_norm[np.isinf(price_norm)] = np.nan
        price_norm = pd.DataFrame(price_norm, columns = price_avg.columns, index = price_avg.index)

        alpha = Util.array_coef(price_norm.tail(n), turn_norm.tail(n))
        return alpha

    def reform(self, temp_result):
        return -temp_result.rolling(self.n).mean() / temp_result.rolling(self.n).std()       



    # def definition(self, amt_by_yuan, free_float_cap, close, adjfactor, is_valid_raw, n=10):

    #     turn = amt_by_yuan[is_valid_raw==1] / free_float_cap
    #     turn_avg = turn.rolling(window=n, min_periods=n).mean()
    #     turn_std = turn.rolling(window=n, min_periods=n).std()
    #     turn_norm = (turn - turn_avg) / turn_std
    #     turn_norm[np.isinf(turn_norm.values)] = np.nan

    #     price = close[is_valid_raw==1] * adjfactor
    #     price_avg = price.rolling(window=n, min_periods=n).mean()
    #     price_std = price.rolling(window=n, min_periods=n).std()
    #     price_norm = (price - price_avg) / price_std
    #     price_norm[np.isinf(price_norm.values)] = np.nan

    #     alpha = -1 * price_norm.rolling(window=n, min_periods=n).corr(turn_norm)
    #     alpha = alpha.rolling(window=n, min_periods=n).mean() / alpha.rolling(window=n, min_periods=n).std()
    #     return alpha
        