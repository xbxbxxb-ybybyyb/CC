from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from scipy.stats import skew
from scipy.stats import kurtosis
from xfactor.FixUtil import minute_data_transform
from xfactor.FixUtil import min_forward_adj
from xfactor.Util import data_filter
from xfactor.Util import rolling_process


class VNSPMean_1_5(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # fix_times = ["1000"]
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.limit_status_minute", "FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute",
                   "FactorData.Basic_factor.turn"]
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
        mvolume = data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'].copy(), limits, 'minute')
        turn = database.depend_data['FactorData.Basic_factor.turn'].copy()
        n = 1
        m = 5

        mclose_rpl = mclose.resample(str(m)+'T').asfreq().dropna(how='all', axis=0)  # 取出m分钟close
        mvolume_rpl = mvolume.resample(str(m)+'T').mean().reindex(index=mclose_rpl.index.to_list())  # 取m分钟的平均换手率作为该分钟的换手率
        mclose_rpl = mclose_rpl.values[-237*n//m:, :]  # 取出n天
        mvolume_rpl = mvolume_rpl.values[-237*n//m:, :]  # 取出n天

        # 因为没有分钟频的换手率，根据前一天的换手率，将当前窗口的缩放到均值为前一天的换手率
        turn = turn.values[-1, :]
        scale = np.nansum(mvolume_rpl, axis=0) / turn / mvolume_rpl.shape[0]
        np.place(scale, scale == 0, np.nan)
        mturn = mvolume_rpl / scale

        # 出现小于等于0的用整列最小值（大于零）代替
        mturn_reverse = mturn[range(mturn.shape[0]-1, -1, -1), :]  # reverse
        mturn_reverse_1 = 1 - mturn_reverse
        temp_turn = mturn_reverse_1.copy()
        np.place(temp_turn, temp_turn <= 0, np.nan)
        mturn_reverse_1 = np.clip(mturn_reverse_1, np.nanmin(temp_turn, axis=0), np.nanmax(temp_turn, axis=0))

        # 求换手率构造的权重
        w = np.nancumprod(mturn_reverse_1, axis=0)
        w = w / (1 - mturn_reverse) * mturn_reverse
        w = w / np.nansum(w, axis=0)
        w_reverse = w[range(mturn.shape[0]-1, -1, -1), :]
        w_reverse = w_reverse[:-1, :]

        mrtns = mclose_rpl[-1, :] / mclose_rpl[:-1, :] - 1

        # 加权平均
        alpha = np.nansum(np.abs(w_reverse * mrtns * 100), axis=0)
        ind = np.nansum(np.isnan(mvolume_rpl), axis=0) >= mvolume_rpl.shape[0] // 2
        alpha[ind] = np.nan
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
