from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd

# #    ["FactorDailyNetworkDegree", {'n': 0.7, 'Data_Base': ['play_day_close', 'play_day_volume'], 'play_day_lag': 11,
#     'play_min_lag': None, 'generator_lag': 1, 'type': 1500},"F_D_NetworkDegree.h5"],
class NetworkDegree(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close","FactorData.Basic_factor.volume",'FactorData.Basic_factor.adjfactor']
    #依赖的个人因子库的因子，默认为空，可不设置
    depend_factors = []
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 10
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 1

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor'].copy()
        close = database.depend_data['FactorData.Basic_factor.close'].copy()*adjfactor
        volume = database.depend_data['FactorData.Basic_factor.volume']
        ret = close/close.shift(1) - 1
        ret = ret * volume/volume
        ret = ret.iloc[-10:, :]
        cor = abs(ret.corr())
        threshold = 0.7
        degree_num = np.zeros(cor.shape)
        degree_num[cor.values > threshold] = 1
        degree_num[cor.values <= threshold] = 0
        ans = pd.Series(degree_num.sum(axis=1)-1,index=close.columns)
        return ans


