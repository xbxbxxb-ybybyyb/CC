from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj


class VolaRatio10Mean(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=1
    reform_window=10
    factype='mean'

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["", ""])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']


        close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        close = min_forward_adj(close)
        close_prev = close.iloc[:242*(self.lag), :]
        ret_prev = pd.DataFrame(close_prev.values[1:, :]/close_prev.values[:-1, :] - 1,
                                index=close_prev.index[1:], columns=close_prev.columns)
        vola_prev = pd.DataFrame(ret_prev.values**2, index=ret_prev.index, columns=ret_prev.columns).sum(axis=0)
        close_today = close.iloc[242*(self.lag):, :]
        ret_today = pd.DataFrame(close_today.values[1:, :]/close_today.values[:-1, :] - 1,
                                 index=close_today.index[1:], columns=close_today.columns)
        ret_selected = ret_today
        vola_today = pd.DataFrame(ret_selected.values**2, index=ret_selected.index,
                                  columns=ret_selected.columns).sum(axis=0)
        ans = vola_today/vola_prev
        ans[np.isinf(ans.values)] = np.nan
        return ans

    def reform(self, temp_result):
        ans = temp_result
        if self.factype == 'mean':
            alpha = ans.rolling(self.reform_window, min_periods=int(self.reform_window/2)).mean()
        elif self.factype == 'std':
            alpha = ans.rolling(self.reform_window, min_periods=int(self.reform_window / 2)).std()
        return alpha


