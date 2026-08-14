from xfactor.BaseFactor import BaseFactor
import numpy as np
import xfactor.Util as ut


class OBCVPema_10(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume_minute"]
    # 依赖的个人因子库的因子，默认为空，可不设置
    # depend_factors = ["SampleFactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0

    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 10

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        volume_min = database.depend_data['FactorData.Basic_factor.volume_minute']
        ocvp = volume_min.iloc[1,:]/volume_min.sum()
        bcvp = volume_min.iloc[-5:].sum()/volume_min.sum()
        ans = ocvp.mul(0.5) + bcvp.mul(0.5)
        return -ans

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()