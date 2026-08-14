# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd

class AmtRet5d(BaseFactor):

    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_badj", "FactorData.Basic_factor.amt"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 10
    reform_window = 60
    def calc_single(self, database):

        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        amt = database.depend_data['FactorData.Basic_factor.amt']
        n = self.lag
        re = (close_adj.iloc[-1,:]-close_adj.iloc[-n-1,:])/close_adj.iloc[-n-1,:]
        re_sign_negative = pd.Series(-1, index = close_adj.columns)
        re_sign_positive = pd.Series(1, index = close_adj.columns)
        # re_sign = (re_sign_positive[re>=0].fillna(0)+re_sign_negative[re<0].fillna(0))
        # re_sign = (re_sign_positive[re>=0]).fillna(0) + (re_sign_negative[re<0]).fillna(0)
        re_sign = (re_sign_positive*(re>=0))*1. + (re_sign_negative*(re<0))*1.

        # amt_valid = amt[is_valid_raw==1]
        # result = (np.log((amt_valid-amt_valid.shift(n))/amt_valid.shift(n)+1)*re_sign).rolling(window=20).sum()
        amt_valid = amt
        result = (amt_valid.iloc[-1,:]-amt_valid.iloc[-n-1,:])/amt_valid.iloc[-n-1,:]
        result = np.log(result + 1)*re_sign
        # result = result[isValid_include_st ==1]
        return result

    def reform(self, temp_result):
        A = temp_result.rolling(self.reform_window,1).sum()
        return -A