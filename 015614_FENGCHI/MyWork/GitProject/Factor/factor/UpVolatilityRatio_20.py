from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import copy
import xfactor.Util as ut


class UpVolatilityRatio_20(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close", "FactorData.Basic_factor.adjfactor"]
    # 依赖的个人因子库的因子，默认为空，可不设置
    # depend_factors = ["SampleFactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 25

    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 20

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        close_non = database.depend_data['FactorData.Basic_factor.close']
        close = close_non * adj
        ret: pd.DataFrame = close / close.shift(1)
        ret_log = pd.DataFrame(np.log(ret.values), index=ret.index, columns=ret.columns)
        ret_log: pd.DataFrame = 1000 * ret_log * ret_log
        original_ret_log = copy.deepcopy(ret_log)
        condition = ret < 1
        ret_log[condition == True] = 0
        ret_log = ret_log.rolling(window=20, min_periods=1).sum()
        original_ret_log = original_ret_log.rolling(window=20, min_periods=1).sum()
        factor_data = ret_log / original_ret_log
        ans = factor_data.iloc[-1, :]
        return -ans

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()

