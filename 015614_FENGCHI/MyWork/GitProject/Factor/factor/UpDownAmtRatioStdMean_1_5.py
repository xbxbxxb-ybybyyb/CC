from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from scipy.stats import skew
from scipy.stats import kurtosis
from xfactor.FixUtil import minute_data_transform
from xfactor.FixUtil import min_forward_adj
from xfactor.Util import data_filter
from xfactor.Util import rolling_process


class UpDownAmtRatioStdMean_1_5(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # fix_times = ["1000"]
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.limit_status_minute", "FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.open_minute",
                   "FactorData.Basic_factor.amt_minute"]
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
        mclose = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'].copy(), limits, 'minute')
        mclose = min_forward_adj(mclose)
        mopen = data_filter(database.depend_data['FactorData.Basic_factor.open_minute'].copy(), limits, 'minute')
        mopen = min_forward_adj(mopen)
        mamt = data_filter(database.depend_data['FactorData.Basic_factor.amt_minute'].copy(), limits, 'minute')
        n = 1
        m = 5
        aggtype = 'std'

        mclose_rpl = mclose.resample(str(m) + 'T').asfreq().dropna(how='all', axis=0)
        mopen_rpl = mopen.resample(str(m) + 'T').asfreq().dropna(how='all', axis=0)
        mamt_rpl = np.sqrt(mamt.resample(str(m) + 'T').sum(min_count=1).reindex(index=mclose_rpl.index.to_list()))

        mamt_long = np.ones(mamt_rpl.shape) * np.nan
        mamt_long[mclose_rpl.values > mopen_rpl.values] = mamt_rpl.values[mclose_rpl.values > mopen_rpl.values]  # 多头成交量
        mamt_short = np.ones(mamt_rpl.shape) * np.nan
        mamt_short[mclose_rpl.values < mopen_rpl.values] = mamt_rpl.values[
            mclose_rpl.values < mopen_rpl.values]  # 空头成交量
        mamt_long = mamt_long[-237 * n // m:, :]  # 取出n天
        mamt_short = mamt_short[-237 * n // m:, :]  # 取出n天

        if aggtype == 'std':
            alpha = np.nanstd(mamt_long, axis=0) / np.nanstd(mamt_short, axis=0)
        elif aggtype == 'skew':
            alpha = skew(mamt_long, axis=0, nan_policy='omit').__array__() / skew(mamt_short, axis=0,
                                                                                  nan_policy='omit').__array__()
        elif aggtype == 'kurt':
            alpha = kurtosis(mamt_long, axis=0, nan_policy='omit').__array__() / kurtosis(mamt_short, axis=0,
                                                                                          nan_policy='omit').__array__()
        else:
            raise ValueError('Unknown aggregation type.')

        np.place(alpha, np.isinf(alpha), np.nan)
        alpha = pd.Series(alpha, index=mclose.columns.to_list())

        return alpha

    def reform(self, temp_result):
        min_periods = self.decide_min_periods('mean', 5)
        factor_values = rolling_process(temp_result, 'mean', window=5, min_periods=min_periods)
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
# ! /usr/bin/env python3
# ! -*- coding:utf-8 -*-
