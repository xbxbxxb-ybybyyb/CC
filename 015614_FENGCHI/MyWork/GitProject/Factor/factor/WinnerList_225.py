from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd


class WinnerList_225(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.pct_chg"]
    #依赖的个人因子库的因子，默认为空，可不设置
    depend_factors = []
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 22

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        pct_chg = database.depend_data['FactorData.Basic_factor.pct_chg']
        ans = pd.Series(pct_chg.rank(axis=1, ascending=False).values[0],index=pct_chg.columns)
        return -ans

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
         return temp_result.rolling(self.reform_window).apply(self.weighted_smaller_than_n)

    def weighted_smaller_than_n(self,series, m=225):
        num = series <= m  # 序列中小于n的次数
        weight = np.arange(1, (22 + 1), 1) / 22
        temp = (num * weight).sum()  # 序列中小于n的加权次数
        return temp