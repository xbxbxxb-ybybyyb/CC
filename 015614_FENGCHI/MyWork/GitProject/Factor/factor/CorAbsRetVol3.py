from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj



class CorAbsRetVol3(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    #fix_times = ["1000", "1030",'1100','1300','1330','1400','1430']
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.volume_minute"]
    #依赖的个人因子库的因子，默认为空，可不设置
    depend_factors = []
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 1
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 3

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        minute_data_transform(database.depend_data,['drop','drop'])
        period = '5min'
        close = database.depend_data["FactorData.Basic_factor.close_minute"].copy()
        ret = np.log(close/close.shift(1))
        ret.iloc[237, :] = np.nan
        ret = ret.iloc[-237*(self.lag):, :].copy()
        close = close.iloc[-237*(self.lag):, :].copy()
        volume = database.depend_data["FactorData.Basic_factor.volume_minute"].iloc[-237*(self.lag):, :].copy()
        filter_index = close.resample(period, how='last').dropna(how='all').index
        ret_min_abs = abs(ret.resample(period).sum().reindex(filter_index))
        volume_min = volume.resample(period).sum().reindex(filter_index)
        ans = pd.Series(-1 * self.cor(ret_min_abs.values,volume_min.values), index=volume.columns)
        return ans

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        alpha = temp_result.rolling(self.reform_window, min_periods=int(self.reform_window-1)).mean()
        return alpha

    def cor(self, x: np.array, y: np.array):
        delta_x = x - np.nanmean(x, axis=0)
        delta_y = y - np.nanmean(y, axis=0)
        corelation = np.nanmean(delta_x * delta_y, axis=0)/(np.nanstd(delta_x, axis=0) * np.nanstd(delta_y, axis=0))
        corelation[np.isinf(corelation)] = np.nan
        return corelation
