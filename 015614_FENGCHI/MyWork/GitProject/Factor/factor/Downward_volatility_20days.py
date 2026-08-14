from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import numpy as np
import pandas as pd
class Downward_volatility_20days(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute"]
    #依赖的个人因子库的因子，默认为空，可不设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 20

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        minute_data_transform(database.depend_data)
        minute_close = min_forward_adj(database.depend_data['FactorData.Basic_factor.close_minute'].copy())
        ret = np.log(minute_close / minute_close.shift(1))
        filter_index = np.zeros(ret.shape)
        filter_index[ret.values < 0] = 1
        vola = ret**2
        ans = (vola*filter_index).sum()/vola.sum()
        return ans

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()

