# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd

class VwapTurnStdRatio(BaseFactor):
    """
    *因子名 : VwapTurnStdRatio
    *因子功能描述 : 取n日vwap标准差与换手表准差之比，求平方

    *因子参数 : turn -- 换手率，vwap -- 均价， n -- 取平均天数
    *作者 : 徐志鑫
    *因子创建日期 : 2019.02.18
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 : 尚未修改
    """

    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.vwap", "FactorData.Basic_factor.turn"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 99

    def calc_single(self, database):
        n = 100
        turn = database.depend_data['FactorData.Basic_factor.turn']
        vwap = database.depend_data['FactorData.Basic_factor.vwap']
        # turn_std = turn.rolling(n).std()
        turn_std = turn.iloc[-n:,:].std()
        
        # vwap_std = vwap.rolling(n).std()
        # vwap_mean = vwap.rolling(n).mean()
        vwap_std = vwap.iloc[-n:,:].std()
        vwap_mean = vwap.iloc[-n:,:].mean()
        
        ratio = np.square((vwap_std / vwap_mean) / turn_std)
        ratio[np.isnan(ratio)] = 0
        
        return ratio

        
