from xfactor.BaseFactor import BaseFactor
from xfactor.Util import rolling_process
from xfactor.FixUtil import min_forward_adj
from xfactor.Util import data_filter
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
from scipy.stats import kurtosis
from scipy.stats import skew


class MinRetVolMaxSr_1_5(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute"]
    # 依赖的个人因子库的因子，默认为空，可不设置
    # depend_factors = ["SampleFactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 1
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 5

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=['drop1', 'drop4'])
        mclose = database.depend_data['FactorData.Basic_factor.close_minute'].copy()
        mclose = min_forward_adj(mclose)
        mvolume = database.depend_data['FactorData.Basic_factor.volume_minute'].copy()

        mclose = mclose.resample('5T').asfreq().dropna(how='all', axis=0)  # 取出m分钟close
        mrtns = np.divide(np.diff(mclose.values, axis=0), mclose.values[:-1, :])  # m分钟收益率
        mvolume = mvolume.resample('5T').sum(min_count=1)  # 取出m分钟volume
        mvolume = mvolume.reindex(index=mclose.index.to_list()[1:], columns=mclose.columns.to_list())
        mrev = np.multiply(mrtns, mvolume.values)  # 收益
        mrev = np.divide(np.multiply(mrev, mvolume.values), mvolume.values)  # 成交量为0的置为nan
        mrev = mrev[-237//5:, :]  # 取出n天

        alpha = self.agg(mrev, 'max')
        alpha = pd.Series(alpha, index=mclose.columns.to_list())

        return alpha

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        min_periods = self.decide_min_periods('sr', 5)
        factor_values = rolling_process(temp_result, 'sr', window=5, min_periods=min_periods)
        factor_values = factor_values.replace(np.inf, np.nan)
        factor_values = factor_values.replace(-np.inf, np.nan)
        return factor_values

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

    @staticmethod
    def decide_min_periods(ptype, window):
        if ptype == 'mean':
            min_periods = 1
        elif ptype in ['std', 'skew', 'kurt', 'sr', 'max', 'min', 'dif']:
            min_periods = window // 2
        else:
            min_periods = None
        return min_periods
