from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
from xfactor.Util import data_filter
from xfactor.Util import rolling_process


class EVolChgBetaAbs_1_1(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # fix_times = ["1030"]
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.limit_status_minute", "FactorData.Basic_factor.volume_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 1
    reform_window = 5

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        # 分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        # 处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation=['drop1', 'drop4'])
        limits = database.depend_data['FactorData.Basic_factor.limit_status_minute']
        mvolume = data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'].copy(), limits, 'minute')

        mvolume_v = mvolume.values[-237:, :]
        alpha = np.nanmax(mvolume_v, axis=0) - np.nanmin(mvolume_v, axis=0)
        ind = np.sum(mvolume_v == 0, axis=0) > (mvolume_v.shape[0] // 2)
        alpha[ind] = np.nan  # 控制0数量，超过一半是0认为这个值是无效的，置为np.nan
        alpha = pd.Series(alpha, index=mvolume.columns.to_list())

        return alpha

    def reform(self, temp_result):
        min_periods = self.decide_min_periods('regbeta', 5)
        factor_values = rolling_process(temp_result, 'regbeta', window=5, min_periods=min_periods)
        factor_values = factor_values.sub(factor_values.mean(axis=1), axis=0).div(factor_values.std(axis=1), axis=0)
        factor_values = factor_values.abs()
        factor_values = factor_values.replace(np.inf, np.nan)
        factor_values = factor_values.replace(-np.inf, np.nan)
        return factor_values

    @staticmethod
    def decide_min_periods(ptype, window):
        if ptype == 'mean':
            min_periods = 1
        elif ptype in ['std', 'skew', 'kurt', 'sr', 'max', 'min', 'dif']:
            min_periods = window // 2
        else:
            min_periods = None
        return min_periods

