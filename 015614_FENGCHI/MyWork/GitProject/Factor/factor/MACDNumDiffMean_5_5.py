from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
from xfactor.FixUtil import min_forward_adj
from xfactor.Util import data_filter
from xfactor.Util import rolling_process


class MACDNumDiffMean_5_5(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # fix_times = ["1000"]
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.limit_status_minute", "FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 6
    reform_window = 5

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        # 分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        # 处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation=['drop1', 'drop4'])
        limits = database.depend_data['FactorData.Basic_factor.limit_status_minute']
        mclose = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'].copy(), limits, 'minute')
        mclose = min_forward_adj(mclose)

        mclose_rpl = mclose.resample('5T').asfreq().dropna(how='all', axis=0)  # 取出m分钟close
        mclose_ma12 = mclose_rpl.rolling(window=12, min_periods=12).mean()
        mclose_ma26 = mclose_rpl.rolling(window=26, min_periods=26).mean()
        dif = mclose_ma12.sub(mclose_ma26)
        dea = dif.rolling(window=9, min_periods=9).mean()
        macd = np.subtract(dif.values, dea.values) * 2  # 求MACD柱
        macd = macd[-237:, :]  # 取出n天的MACD柱

        alpha = np.nansum(macd > 0, axis=0) - np.nansum(macd < 0, axis=0)  # 这里出现的很多0是由于macd全都是nan导致的
        alpha = pd.Series(alpha, index=mclose.columns.to_list())
        ind = np.nansum(np.isnan(macd), axis=0) > (macd.shape[0] // 2)
        alpha[ind] = np.nan  # MACD柱nan数量超过一半的直接置为np.nan

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

