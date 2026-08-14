from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj


class Vwap2Twap5mean(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=1
    reform_window=5
    process='mean'
    period=5
    factype='mean'

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']


        # 数据通过self.data_base字典获取
        amt = data_filter(database.depend_data['FactorData.Basic_factor.amt_minute'].iloc[-237:, :].copy(),limit_status,method='minute')
        volume = data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'].iloc[-237:, :].copy(),limit_status,method='minute')
        close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        close = min_forward_adj(close)
        close = close.iloc[-237:, :].copy()
        period = str(self.period)+'min'
        twap_min = close.resample(period).mean()
        amt_min = amt.resample(period).sum()
        volume_min = volume.resample(period).sum()
        vwap_min = amt_min/volume_min
        vwap_min = vwap_min.dropna(how='all')
        vwap_min = min_forward_adj(vwap_min)
        twap_min = twap_min.reindex(vwap_min.index)
        diff = vwap_min - twap_min
        if self.factype == 'mean':
            ans = diff.mean()
        elif self.factype == 'std':
            ans = diff.std()
        elif self.factype == 'skew':
            ans = diff.skew()
        elif self.factype == 'kurt':
            ans = diff.kurt()
        return ans



    def reform(self, temp_result):
        temp = temp_result
        if self.process == 'mean':
            alpha = temp.rolling(self.reform_window, min_periods=int(self.reform_window/2)).mean()
        elif self.process == 'std':
            alpha = temp.rolling(self.reform_window, min_periods=int(self.reform_window / 2)).std()
        return  alpha


