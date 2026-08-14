from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd

class GTJA36(BaseFactor):
    #  定义因子参数

    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume", "FactorData.Basic_factor.vwap",
                   'FactorData.Basic_factor.adjfactor']
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 5
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 2

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        vwap = database.depend_data['FactorData.Basic_factor.vwap'].copy()
        volume = database.depend_data['FactorData.Basic_factor.volume'].copy()
        volume_rk = volume.rank(axis=1)
        vwap_rk = vwap.rank(axis=1)
        ans = pd.Series(self.__cor(volume_rk.values, vwap_rk.values), index=vwap.columns)
        return ans


    def __cor(self,x: np.array, y: np.array):
        delta_x = x - np.nanmean(x, axis=0)
        delta_y = y - np.nanmean(y, axis=0)
        corelation = np.nanmean(delta_x * delta_y, axis=0) / (
                    np.nanstd(delta_x, axis=0) * np.nanstd(delta_y, axis=0))
        corelation[np.isinf(corelation)] = np.nan
        return -corelation

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean().rank(axis=1)