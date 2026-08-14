from xfactor.BaseFactor import BaseFactor
import numpy as np
import xfactor.Util as ut


class TPVDeltaCorr(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.close_minute"]
    # 依赖的个人因子库的因子，默认为空，可不设置
    # depend_factors = ["SampleFactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0

    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 1

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        minute_volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_volume_delta = minute_volume - minute_volume.shift(1)
        minute_close_delta = minute_close - minute_close.shift(1)

        ans = ut.array_coef(minute_volume_delta.iloc[-15:,:], minute_close_delta.iloc[-15:,:])
        return -ans

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()