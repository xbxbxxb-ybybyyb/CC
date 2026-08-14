from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import statsmodels.api as sm
from copy import deepcopy
import pandas as pd

class High2LowVolDown(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.close_minute","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag =0

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']

        volume_df = data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'],limit_status,method='minute')
        close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        close_df=min_forward_adj(close)
        close_low = close_df.rolling(15, min_periods=12).min()
        close_high = close_df.rolling(15, min_periods=12).max()

        min_high = pd.DataFrame(np.array([close_low.max()] * close_df.shape[0]), index=close_df.index,
                                columns=close_df.columns)
        max_low = pd.DataFrame(np.array([close_high.min()] * close_df.shape[0]), index=close_df.index,
                               columns=close_df.columns)

        high_vol_down = volume_df[np.logical_and(close_df<close_df.shift(1), close_df >= min_high)].mean()
        low_vol_down = volume_df[np.logical_and(close_df<close_df.shift(1), close_df <= max_low)].mean()

        ans = np.divide(high_vol_down, low_vol_down)
        return ans


