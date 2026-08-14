from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import statsmodels.api as sm
from copy import deepcopy
import pandas as pd

class VwapSwingCorr(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high_minute","FactorData.Basic_factor.low_minute","FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag =0

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        def cor(x: np.array, y: np.array):
            delta_x = x - np.nanmean(x, axis=0)
            delta_y = y - np.nanmean(y, axis=0)
            correlation = np.nanmean(delta_x * delta_y, axis=0) / (
                        np.nanstd(delta_x, axis=0) * np.nanstd(delta_y, axis=0))
            correlation[np.isinf(correlation)] = np.nan
            return correlation
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']

        amt_df = data_filter(database.depend_data['FactorData.Basic_factor.amt_minute'].copy(),limit_status,method='minute')
        volume_df = data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'].copy(),limit_status,method='minute')
        high = data_filter(database.depend_data['FactorData.Basic_factor.high_minute'].copy(),limit_status,method='minute')
        high_df=min_forward_adj(high)
        low = data_filter(database.depend_data['FactorData.Basic_factor.low_minute'].copy(),limit_status,method='minute')
        low_df=min_forward_adj(low)
        vwap_df = np.divide(amt_df, volume_df)
        swing_df = np.divide(np.subtract(high_df, low_df), low_df)
        ans = pd.Series(cor(vwap_df, swing_df), index=list(vwap_df.columns))
        return ans

