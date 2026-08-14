from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform,min_forward_adj


class BSPowerSkew3mean(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=1
    reform_window=3
    process='mean'
    period=5
    factype='skew'

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']


        close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'].copy(),limit_status,method='minute')
        close = min_forward_adj(close)
        ret_period = np.log(close/close.shift(self.period)).iloc[-237:, :].copy()
        period = str(self.period)+'min'
        ret_period_max = ret_period.resample(period).max()
        ret_period_min = ret_period.resample(period).min()
        ret_period_diff = ret_period_max - ret_period_min
        ret_period_diff[ret_period_diff.values == 0] = np.nan
        if self.factype == 'mean':
            ans = ret_period_diff.mean()
        elif self.factype == 'std':
            ans = ret_period_diff.std()
        elif self.factype == 'skew':
            ans = ret_period_diff.skew()
        elif self.factype == 'kurt':
            ans = ret_period_diff.kurt()
        return ans

    def reform(self, temp_result):
        ans = temp_result
        if self.process == 'mean':
            alpha = ans.rolling(self.reform_window,min_periods=int(self.reform_window/2)).mean()
        elif self.process == 'std':
            alpha = ans.rolling(self.reform_window,min_periods=int(self.reform_window/2)).std()
        return alpha


