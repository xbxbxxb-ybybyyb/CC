from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform,min_forward_adj


class OCKurt3mean(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.open_minute","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=1
    reform_window=3
    process='mean'
    period=5
    factype='kurt'

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']


        close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        close = min_forward_adj(close)
        close =close.iloc[-(self.lag)*237:, :].copy()
        open = data_filter(database.depend_data['FactorData.Basic_factor.open_minute'],limit_status,method='minute')
        open = min_forward_adj(open)
        open = open.iloc[-237:, :].copy()
        period = str(self.period)+'min'
        close_min = close.resample(period,how='last')
        close_min = close_min.dropna(how='all')
        open_min = open.resample(period,how='first')
        open_min = open_min.dropna(how='all')
        kline_range = abs(close_min-open_min)
        if self.factype == 'std':
            ans = kline_range.std()
        elif self.factype == 'mean':
            ans = kline_range.mean()
        elif self.factype == 'skew':
            ans = kline_range.skew()
        elif self.factype == 'kurt':
            ans = kline_range.kurt()
        elif self.factype == 'sharpe':
            ans = kline_range.mean()/kline_range.std()
        elif self.factype == 'stdratio':
            ans = kline_range.std()/kline_range.mean()
        return ans

    def reform(self, temp_result):
        ans = temp_result
        if self.process == 'mean':
            alpha = ans.rolling(self.reform_window, min_periods=int(self.reform_window/2)).mean()
        return alpha


