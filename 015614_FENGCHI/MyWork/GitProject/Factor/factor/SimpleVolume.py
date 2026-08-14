# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd

class SimpleVolume(BaseFactor):
    """
    *因子名 : SimpleVolume
    *因子功能描述:每单位交易量推动的收益率
    *因子参数 : close_adj-收盘价,volume-成交量,is_valid_raw-股票状态
    *作者 : hezq
    *因子创建日期 : 2019.04.10
    """
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_badj", "FactorData.Basic_factor.volume"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 5
    reform_window = 5

    def calc_single(self, database):
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        volume = database.depend_data['FactorData.Basic_factor.volume']

        d = 5
        # pct = close_adj/close_adj.shift(1)-1
        arr = close_adj.values / close_adj.shift(1).values - 1
        pct = pd.DataFrame(arr, index=close_adj.index, columns=close_adj.columns)

        arr = pct.values / volume.values * 10000
        factor = pd.DataFrame(arr, index=pct.index, columns=pct.columns)

        # factor = factor[is_valid_raw==1].rolling(window=d,min_periods=1).mean()
        # factor = factor[is_valid_raw==1]
        return -factor.iloc[-1, :]

    def reform(self, temp_result):
        A = temp_result.rolling(self.reform_window, min_periods=1).mean()
        return A