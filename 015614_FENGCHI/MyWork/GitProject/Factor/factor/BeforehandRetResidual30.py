from xfactor.BaseFactor import BaseFactor
import statsmodels.api as sm
from copy import deepcopy
from datetime import datetime
import time
import pandas as pd
import numpy as np
from xfactor.FixUtil import min_forward_adj

class BeforehandRetResidual30(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close","FactorData.Basic_factor.adjfactor","FactorData.Basic_factor.turn"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 48
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 1

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        adj_factor = database.depend_data['FactorData.Basic_factor.adjfactor']
        close = database.depend_data['FactorData.Basic_factor.close']*adj_factor
        turn = database.depend_data['FactorData.Basic_factor.turn']*adj_factor
        turn_residual = turn.rolling(20).apply(self.cal_residual)
        ret = close.pct_change(periods=1).iloc[19:]
        turn_residual = turn_residual.iloc[19:]
        corr_ret_turn_residual = ret.corrwith(turn_residual)
        return -corr_ret_turn_residual

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()

    def cal_residual(self, data_array):
        x = data_array[:-1]
        y = data_array[1:]
        beta = y.std() / x.std() * np.corrcoef(x,y)[0,1]
        alpha = y.mean() - beta * x.mean()
        residual = y[-1] - (alpha + beta * x[-1])
        return residual