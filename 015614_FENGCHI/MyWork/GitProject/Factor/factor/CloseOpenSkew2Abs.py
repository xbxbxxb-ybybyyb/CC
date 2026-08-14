from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from scipy.stats import skew
from xfactor.FixUtil import minute_data_transform
from xfactor.FixUtil import min_forward_adj
from xfactor.Util import data_filter


class CloseOpenSkew2Abs(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # fix_times = ["1030"]
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.limit_status_minute", "FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.open_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 2
    reform_window = 1

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation=['drop1', 'drop4'])
        limits = database.depend_data['FactorData.Basic_factor.limit_status_minute']
        mclose = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'].copy(), limits, 'minute')
        mopen = data_filter(database.depend_data['FactorData.Basic_factor.open_minute'].copy(), limits, 'minute')
        mclose = min_forward_adj(mclose)
        mopen = min_forward_adj(mopen)

        alpha = np.abs(skew(mclose.values / mopen.values, axis=0, nan_policy='omit'))
        alpha = pd.Series(alpha, index=mclose.columns.to_list())

        return alpha