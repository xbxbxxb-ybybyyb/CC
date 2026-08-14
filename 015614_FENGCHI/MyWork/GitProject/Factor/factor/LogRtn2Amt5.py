from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
from xfactor.FixUtil import min_forward_adj
from xfactor.Util import data_filter


class LogRtn2Amt5(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # fix_times = ["1000"]
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.limit_status_minute", "FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.amt_minute"]
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
        mamt = data_filter(database.depend_data['FactorData.Basic_factor.amt_minute'].copy(), limits, 'minute')

        mclose5m = mclose.iloc[-237*5:, :].resample('5T').asfreq().dropna(axis=0, how='all')  # 取出5min的close
        mrtns5m = mclose5m.values[1:, :] / mclose5m.values[:-1, :] - 1    # 5min收益率
        rtns = np.log(np.prod(mrtns5m + 1, axis=0))  # 累积对数收益率（绝对值）
        mamt5m = np.nansum(mamt.values[-237*5:, :], axis=0)  # 求n天成交额
        mamt5mscale = mamt5m / np.nansum(mamt5m) * 50  # 进行一定放缩，使得相除值比较正常
        alpha = rtns / mamt5mscale
        alpha = pd.Series(alpha, index=mclose.columns.to_list())

        return alpha

    @staticmethod
    def cal_high_dist(x):
        if np.sum(np.isnan(x)) > len(x) // 2:
            dist = np.nan
        else:
            dist = np.nanargmax(x) / len(x)
        return dist

    @staticmethod
    def decide_min_periods(ptype, window):
        if ptype == 'mean':
            min_periods = 1
        elif ptype in ['std', 'skew', 'kurt', 'sr', 'max', 'min', 'dif']:
            min_periods = window // 2
        else:
            min_periods = None
        return min_periods

