from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import pandas as pd

class PVComb5(BaseFactor):
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
    direction='Down'
    lag=1
    threshold=0.8

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']


        def cor(x: np.array, y: np.array):
            delta_x = x - np.nanmean(x, axis=0)
            delta_y = y - np.nanmean(y, axis=0)
            corelation = np.nanmean(delta_x * delta_y, axis=0) / (
                        np.nanstd(delta_x, axis=0) * np.nanstd(delta_y, axis=0))
            corelation[np.isinf(corelation)] = np.nan
            return corelation
        def zscore(x: pd.Series):
            y = (x.values-x.mean())/x.std()
            y = pd.Series(y,index=x.index)
            return y
        period = str(self.period) + 'min'
        close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        close = min_forward_adj(close)
        close = close.iloc[-237*(self.lag):, :].copy()
        ret = np.log(close/close.shift(1))
        volume = data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'].iloc[-237*(self.lag):, :].copy(),limit_status,method='minute')
        index = close.resample(period,how='last').dropna(how='all').index
        ret_min = ret.resample(period).sum().reindex(index)
        filter = np.zeros(ret_min.shape)
        if self.direction == 'Up':
            filter[ret_min.values > 0] = 1
        elif self.direction == 'Down':
            filter[ret_min.values < 0] = 1
        elif self.direction == 'All':
            filter = np.ones(ret_min.shape)
        ret_min_filter = ret_min * filter / filter
        volume_min = volume.resample(period).sum().reindex(index)
        core = cor(ret_min_filter.values,volume_min.shift(self.lag).values)
        FR = pd.Series(core,index=close.columns)
        twap_min = close.resample(period).mean().dropna(how='all')
        twap_threshold = twap_min.quantile(self.threshold)
        filter = np.zeros(twap_min.shape)
        filter[twap_min.values - twap_threshold.values > 0] = 1
        twap_min_filter = twap_min * filter / filter
        corpvcut = pd.Series(cor(twap_min_filter.values,volume_min.values),index=close.columns)
        ans = zscore(FR) - zscore(corpvcut)
        return ans

    def reform(self, temp_result):
        
        temp = temp_result
        alpha = temp.rolling(self.reform_window,min_periods=int(self.reform_window/2)).mean()
        return alpha


