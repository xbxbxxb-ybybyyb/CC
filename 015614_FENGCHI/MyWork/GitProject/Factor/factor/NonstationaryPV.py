from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import time

class NonstationaryPV(BaseFactor):
    #  定义因子参数

    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close", "FactorData.Basic_factor.volume",
                   "FactorData.Basic_factor.adjfactor","FactorData.Basic_factor.is_valid"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 5

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        volume = database.depend_data['FactorData.Basic_factor.volume'] / adjfactor
        close = database.depend_data['FactorData.Basic_factor.close'] * adjfactor
        Aclose = self.A_compute(close, close)
        Aclose = np.sqrt(Aclose)
        Avolume = self.A_compute(volume, volume)
        Avolume = np.sqrt(Avolume)
        Aclose_volume = self.A_compute(close, volume)
        ans = Aclose_volume / (Aclose * Avolume)
        ans[~np.isfinite(ans)] = np.nan
        ans[is_valid.iloc[-1,:] == 0] == np.nan
        ans.name = close.index[-1]
        return -1 * ans
        
        
    def A_compute(self, x, y):
        x_pre = x.shift(1)
        Ax = x-x_pre
        y_pre = y.shift(1)
        Ay = y-y_pre
        A = Ax * Ay
        A = A.mean()
        return A
