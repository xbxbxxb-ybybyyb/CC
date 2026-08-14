from xfactor.BaseFactor import BaseFactor
import xfactor.Util as ut


class GTJA74(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume_by_share", "FactorData.Basic_factor.low", "FactorData.Basic_factor.vwap"]
    #依赖的个人因子库的因子，默认为空，可不设置
    # depend_factors = ["MinCloseCallAmtRatio"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 65
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    # reform_window = 10

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        low = database.depend_data['FactorData.Basic_factor.low']
        volume = database.depend_data['FactorData.Basic_factor.volume_by_share']
        vwap = database.depend_data['FactorData.Basic_factor.vwap']
        price = low * 0.35 + vwap * 0.65
        price_sum = price.rolling(20).sum()
        volume_mean = volume.rolling(40).mean()
        volume_mean_sum = volume_mean.rolling(20).sum()
        corr1 = ut.rolling_corr(price_sum, volume_mean_sum, 7)
        vwap_rank = vwap.rank(axis=1)
        volume_rank = volume.rank(axis=1)
        corr2 = ut.rolling_corr(vwap_rank, volume_rank, 6)
        ans = corr1.iloc[-1].rank(pct=True) + corr2.iloc[-1].rank(pct=True)
        return -ans

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    # def reform(self, temp_result):
    #     return temp_result.rolling(self.reform_window).mean()
