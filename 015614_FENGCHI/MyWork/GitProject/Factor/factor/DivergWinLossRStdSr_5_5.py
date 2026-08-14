from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from scipy.stats import kurtosis
from scipy.stats import skew
from xfactor.FixUtil import minute_data_transform
from xfactor.FixUtil import min_forward_adj
from xfactor.Util import data_filter
from xfactor.Util import rolling_process


class DivergWinLossRStdSr_5_5(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # fix_times = ["1000"]
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.limit_status_minute", "FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.open_minute",
                   "FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute",
                   "FactorData.Basic_factor.volume_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 5
    reform_window = 5

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation=['drop1', 'drop4'])
        limits = database.depend_data['FactorData.Basic_factor.limit_status_minute']
        mclose = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'].copy(), limits, 'minute')
        mopen = data_filter(database.depend_data['FactorData.Basic_factor.open_minute'].copy(), limits, 'minute')
        mhigh = data_filter(database.depend_data['FactorData.Basic_factor.high_minute'].copy(), limits, 'minute')
        mlow = data_filter(database.depend_data['FactorData.Basic_factor.low_minute'].copy(), limits, 'minute')
        mvolume = data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'].copy(), limits, 'minute')
        mclose = min_forward_adj(mclose)
        mopen = min_forward_adj(mopen)
        mhigh = min_forward_adj(mhigh)
        mlow = min_forward_adj(mlow)
        m = 5

        mclose_rpl = mclose.resample(str(m)+'T').asfreq().dropna(how='all', axis=0)  # 取出m分钟close
        mopen_rpl = mopen.resample(str(m) + 'T').asfreq().dropna(how='all', axis=0)  # 取出m分钟open
        mhigh_rpl = mhigh.resample(str(m) + 'T').asfreq().dropna(how='all', axis=0)  # 取出m分钟high
        mlow_rpl = mlow.resample(str(m) + 'T').asfreq().dropna(how='all', axis=0)  # 取出m分钟low
        mvolume_rpl = mvolume.resample(str(m) + 'T').sum(min_count=1).dropna(how='all', axis=0)  # 取出m分钟volume
        mvolume_rpl = mvolume_rpl.reindex(index=mclose_rpl.index.to_list()).values
        divergence = np.divide(np.subtract(mhigh_rpl.values, mlow_rpl.values), np.abs(np.subtract(mclose_rpl.values, mopen_rpl.values)))  # 分歧程度

        # 出现开盘价等于收盘价的情形，此时divergence为np.inf，用整一行的最大值代替
        ind = np.isinf(divergence)
        temp_divg = divergence[:]
        np.place(temp_divg, ind, np.nan)
        temp_divg_max = np.repeat(np.expand_dims(np.nanmax(temp_divg, axis=1), axis=1), temp_divg.shape[1], axis=1)
        divergence[ind] = temp_divg_max[ind]

        win_loss_rate = np.divide(np.subtract(mclose_rpl.values, mopen_rpl.values), mopen_rpl.values)
        diverg_win_loss = np.multiply(divergence, win_loss_rate*100)
        diverg_win_loss = np.divide(np.multiply(diverg_win_loss, mvolume_rpl), mvolume_rpl)  # 清除成交量为0的
        diverg_win_loss = diverg_win_loss[-237*5//m:, :]  # 取出n天

        alpha = self.agg(diverg_win_loss, 'std')
        alpha = pd.Series(alpha, index=mclose_rpl.columns.to_list())

        return alpha

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

