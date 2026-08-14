from xfactor.BaseFactor import BaseFactor
import numpy as np
import xfactor.Util as ut


class GTJA179(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.amt_by_yuan", "FactorData.Basic_factor.volume_by_share", "FactorData.Basic_factor.low"]
    # 依赖的个人因子库的因子，默认为空，可不设置
    # depend_factors = ["SampleFactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 80

    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 3

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        amt = database.depend_data["FactorData.Basic_factor.amt_by_yuan"]
        volume = database.depend_data["FactorData.Basic_factor.volume_by_share"]
        low = database.depend_data['FactorData.Basic_factor.low']

        vwap = amt/volume
        corr_df1 = ut.rolling_corr(vwap, volume, 4)
        mean_df = volume.rolling(50).mean()
        rank_df3 = mean_df.rank(axis=1)
        rank_df4 = low.rank(axis=1)
        corr_df2 = ut.rolling_corr(rank_df4, rank_df3, 12)
        rank_df2 = corr_df2.rank(axis=1)
        ans = corr_df1 *rank_df2
        ans = ans.iloc[-1, :]
        return -ans

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()

