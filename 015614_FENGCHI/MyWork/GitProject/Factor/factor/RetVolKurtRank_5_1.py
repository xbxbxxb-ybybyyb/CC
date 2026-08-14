from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from scipy.stats import skew
from scipy.stats import kurtosis
from xfactor.FixUtil import minute_data_transform
from xfactor.FixUtil import min_forward_adj
from xfactor.Util import data_filter
from xfactor.Util import rolling_process


class RetVolKurtRank_5_1(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # fix_times = ["1000"]
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.limit_status_minute", "FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 5
    reform_window = 1

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        # 分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        # 处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation=['drop1', 'drop4'])
        limits = database.depend_data['FactorData.Basic_factor.limit_status_minute']
        mclose = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'].copy(), limits, 'minute')
        mclose = min_forward_adj(mclose)
        mvolume = data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'].copy(), limits, 'minute')
        n = 5

        mrtns = np.divide(np.diff(mclose.values, axis=0), mclose.values[:-1, :])  # m分钟收益率
        mvolume_rpl = mvolume.reindex(index=mclose.index.to_list()[1:], columns=mclose.columns.to_list())
        mrev = np.multiply(mrtns, mvolume_rpl.values)  # 收益
        mrev = np.divide(np.multiply(mrev, mvolume_rpl.values), mvolume_rpl.values)  # 成交量为0的置为nan
        mrev = mrev[-237*n:, :]  # 取出n天

        alpha = self.agg(mrev, 'kurt')
        alpha = pd.Series(alpha, index=mclose.columns.to_list())

        return alpha

    def reform(self, temp_result):
        factor_values = rolling_process(temp_result, 'rank', window=1)
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

    @staticmethod
    def agg(factor_array, aggtype):
        if aggtype == 'mean':
            factor_new = np.nanmean(factor_array, axis=0)
        elif aggtype == 'std':
            factor_new = np.nanstd(factor_array, axis=0)
        elif aggtype == 'skew':
            factor_new = skew(factor_array, nan_policy='omit').__array__()
        elif aggtype == 'kurt':
            factor_new = kurtosis(factor_array, nan_policy='omit').__array__()
        elif aggtype == 'max':
            factor_new = np.nanmax(factor_array, axis=0)
        elif aggtype == 'min':
            factor_new = np.nanmin(factor_array, axis=0)
        elif aggtype == 'dif':
            factor_new = np.nanmax(factor_array, axis=0) - np.nanmin(factor_array, axis=0)
        else:
            raise ValueError('Unknown aggregation type.')
        return factor_new