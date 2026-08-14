from xfactor.BaseFactor import BaseFactor
from xfactor.Util import rolling_process
from xfactor.FixUtil import min_forward_adj
from xfactor.Util import data_filter
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
from scipy.stats import kurtosis
from scipy.stats import skew


class MinMACDNumDiffMean_1_1(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute"]
    # 依赖的个人因子库的因子，默认为空，可不设置
    # depend_factors = ["SampleFactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 3
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 5

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=['drop1', 'drop4'])
        mclose = database.depend_data['FactorData.Basic_factor.close_minute'].copy()
        mclose = min_forward_adj(mclose)

        mclose_ma12 = mclose.rolling(window=12, min_periods=12).mean()
        mclose_ma26 = mclose.rolling(window=26, min_periods=26).mean()
        dif = mclose_ma12.sub(mclose_ma26)
        dea = dif.rolling(window=9, min_periods=9).mean()
        macd = np.subtract(dif.values, dea.values) * 2  # 求MACD柱
        macd = macd[-237:, :]  # 取出n天的MACD柱

        alpha = np.nansum(macd > 0, axis=0) - np.nansum(macd < 0, axis=0)  # 这里出现的很多0是由于macd全都是nan导致的
        alpha = pd.Series(alpha, index=mclose.columns.to_list())
        ind = np.nansum(np.isnan(macd), axis=0) > (macd.shape[0] // 2)
        alpha[ind] = np.nan  # MACD柱nan数量超过一半的直接置为np.nan

        return -alpha

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        factor_values = rolling_process(temp_result, 'mean', window=5, min_periods=2)
        factor_values = factor_values.replace(np.inf, np.nan)
        factor_values = factor_values.replace(-np.inf, np.nan)
        return factor_values

