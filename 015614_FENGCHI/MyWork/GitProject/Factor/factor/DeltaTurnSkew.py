# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class DeltaTurnSkew(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.turn"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 22
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    # reform_window = 10

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self,database):
        turn = database.depend_data['FactorData.Basic_factor.turn']
        result = turn.values
        result = pd.DataFrame(result/turn.shift(1).values-1,index=turn.index,columns=turn.columns)
        n=20
        result = -result.iloc[-n:,:].skew()
        return result















