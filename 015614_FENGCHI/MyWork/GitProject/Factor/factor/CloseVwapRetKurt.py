# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np


class CloseVwapRetKurt(BaseFactor):
    # depend_data = ['FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.volume_minute',
    #                'FactorData.Basic_factor.close_minute']
    # factor_type = "DAY"
    # reform_window = 20
    #
    # def calc_single(self, database):
    #     minute_data_transform(database.depend_data, operation=["drop", "merge"])
    #     vol = database.depend_data['FactorData.Basic_factor.volume_minute']
    #     amt = database.depend_data['FactorData.Basic_factor.amt_minute']
    #     close = database.depend_data['FactorData.Basic_factor.close_minute']
    #     res = -(close / (amt.cumsum() / vol.cumsum().replace(0, np.nan)) - 1).kurt()
    #     return res
    #
    # def reform(self, temp_result):
    #     a = np.e ** (np.arange(19, -1, -1) / 5 * np.log(0.5))
    #     alpha = temp_result.rolling(20).apply(lambda x: (x * a).sum())
    #     return alpha

    factor_type = "DAY"
    s_amt_min = 'FactorData.Basic_factor.amt_minute'
    s_volume_min = 'FactorData.Basic_factor.volume_minute'
    s_close_min = 'FactorData.Basic_factor.close_minute'
    depend_data = [s_amt_min, s_volume_min, s_close_min]
    n = 19
    lag = n

    def fun(self, amount, volume, close):
        vwap = amount.cumsum() / volume.cumsum().replace(0, np.nan)  # 滚动成交均价
        return  -(close / vwap - 1).kurt()  # 筹码收益率峰度

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        volume_min = database.depend_data[self.s_volume_min]
        close_min = database.depend_data[self.s_close_min]
        amt_min = database.depend_data[self.s_amt_min]
        n_shares = len(close_min.columns)
        k_0 = np.zeros(shape=(self.n, n_shares))
        for i in range(self.n):
            idx1 = i * 240
            idx2 = idx1 + 240
            tmp = self.fun(amt_min[idx1 : idx2], volume_min[idx1 : idx2], close_min[idx1:idx2])
            k_0[i, :] = tmp
        k_1= self.fun(amt_min[-240:], volume_min.iloc[-240:], close_min.iloc[-240:])
        a = np.e ** (-np.arange(self.n, -1, -1) / 5 * np.log(2)) # 5日半衰期的指数加权权重（回看20日）
        factor = np.dot(a[:self.n], k_0)  + a[-1] * k_1.values
        return pd.Series(factor, index = close_min.columns, name = k_1.name)
