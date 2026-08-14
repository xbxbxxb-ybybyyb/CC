from xfactor.BaseFactor import BaseFactor
import xfactor.Util as ut
import numpy as np


class GTJA64(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume_by_share", "FactorData.Basic_factor.close", "FactorData.Basic_factor.vwap"]
    #依赖的个人因子库的因子，默认为空，可不设置
    # depend_factors = ["MinCloseCallAmtRatio"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 88
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    # reform_window = 10

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        close = database.depend_data['FactorData.Basic_factor.close']
        volume = database.depend_data['FactorData.Basic_factor.volume_by_share']
        linear_seq_4 = np.linspace(1, 4, 4)
        linear_seq_14 = np.linspace(1, 14, 14)
        vwap = database.depend_data['FactorData.Basic_factor.vwap']
        vwap_rank = vwap.rank(axis=1)
        volume_rank = volume.rank(axis=1)
        corr1 = ut.rolling_corr(vwap_rank, volume_rank, 4)
        corr1_mean = corr1.iloc[-4:].mul(linear_seq_4, axis=0).sum() / sum(linear_seq_4)
        corr1_mean_rank = corr1_mean.rank(pct=True)
        close_rank = close.rank(axis=1)
        volume_mean = volume.rolling(60).mean()
        volume_mean_rank = volume_mean.rank(axis=1)
        corr2 = ut.rolling_corr(close_rank, volume_mean_rank, 4)
        corr2_max = corr2.rolling(13).max()
        corr2_max_mean = corr2_max.iloc[-14:].mul(linear_seq_14, axis=0).sum() / sum(linear_seq_14)
        corr2_max_mean_rank = corr2_max_mean.rank(pct=True)
        ans = -np.maximum(corr1_mean_rank, corr2_max_mean_rank)
        return ans

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    # def reform(self, temp_result):
    #     return temp_result.rolling(self.reform_window).mean()
