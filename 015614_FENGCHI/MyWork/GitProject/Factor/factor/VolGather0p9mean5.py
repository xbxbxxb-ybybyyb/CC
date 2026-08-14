from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj


class VolGather0p9mean5(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=1
    reform_window=5
    period=5
    threshold=0.9

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']


        period = str(self.period)+'min'
        close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        close = min_forward_adj(close)
        close = close.iloc[-237*(self.lag):, :].copy()
        volume = data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'].iloc[-237*(self.lag):, :].copy(),limit_status,method='minute')
        ret = np.log(close/close.shift(1))
        index = close.resample(period,how='last').dropna(how='all').index
        ret_min = ret.resample(period).sum().reindex(index)
        volume_min = volume.resample(period).sum().reindex(index)
        threshold = ret_min.quantile(self.threshold)
        filter = np.zeros(ret_min.shape)
        filter[ret_min.values - threshold.values >= 0] = 1
        part1 = pd.DataFrame((volume_min*filter/filter).values**2,index=volume_min.index,columns=volume_min.columns).sum(axis=0)
        part2 = pd.DataFrame(volume_min.values**2,index=volume_min.index,columns=volume_min.columns).sum(axis=0)
        ans = part1/part2
        return ans

    def reform(self, temp_result):
        ans = temp_result
        alpha = ans.rolling(self.reform_window,min_periods=int(self.reform_window/2)).mean()
        return alpha


