from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import pandas as pd

class Cor300Down5mean(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.close-index_minute","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=1
    reform_window=5
    benchmark='000300.SH'
    direction='down'
    ret_min=15
    process='mean'

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
        close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'].copy(),limit_status,method='minute')
        close = min_forward_adj(close)
        close_bench = data_filter(database.depend_data['FactorData.Basic_factor.close-index_minute'],limit_status,method='minute')
        close_bench = close_bench.loc[:, self.benchmark:self.benchmark]
        ret = np.log(close/close.shift(self.ret_min))
        ret_bench = np.log(close_bench/close_bench.shift(self.ret_min))
        na_index = np.arange(237,237+self.ret_min,1)
        ret.iloc[na_index, :] = np.nan
        ret = ret.iloc[-237:, :].copy()
        ret_bench.iloc[na_index, :] = np.nan
        ret_bench = ret_bench.iloc[-237:, :]
        up_filter = np.zeros(ret_bench.shape)
        down_filter = np.zeros(ret_bench.shape)
        up_filter[ret_bench.values > 0] = 1
        down_filter[ret_bench.values < 0] = 1
        cor_up = cor((ret*up_filter/up_filter).values,(ret_bench*up_filter/up_filter).values)
        cor_down = cor((ret*down_filter/down_filter).values,(ret_bench*down_filter/down_filter).values)
        if self.direction == 'up':
            ans = pd.Series(cor_up, index=ret.columns)
        elif self.direction == 'down':
            ans = pd.Series(cor_down, index=ret.columns)
        elif self.direction == 'net':
            ans = pd.Series(cor_up-cor_down, index=ret.columns)
        return ans

    def reform(self, temp_result):
        temp = temp_result
        if self.process == 'mean':
            alpha = temp.rolling(self.reform_window, min_periods=int(self.reform_window/2)).mean()
        return alpha


