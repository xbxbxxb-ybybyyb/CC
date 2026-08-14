# import sys
# sys.path.insert(0, '/data/group/800020/AlphaFramework/FactorManagement/')
# from AlphaFactor import *


from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np

class GTJA_026(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close", "FactorData.Basic_factor.vwap","FactorData.Basic_factor.adjfactor",]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 250
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    # reform_window = 10

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        n = 7
        n1 = 5
        n2 = 230
        vwap = database.depend_data['FactorData.Basic_factor.vwap']
        close = database.depend_data['FactorData.Basic_factor.close']
        adjf = database.depend_data['FactorData.Basic_factor.adjfactor']
        close_adj = close * adjf
        vwap_adj = vwap * adjf
        
        # close_ma = close_adj.rolling(window=n, center=False, min_periods=int(0.8*n)).mean()
        close_ma = close_adj.iloc[-n:,].mean()
        # part1 = (close_ma - close_adj)/close_ma
        part1 = (close_ma - close_adj.iloc[-1,])/close_ma
        # delay = close_adj.shift(n1)
        delay = close_adj.shift(n1)
        # part2 = vwap_adj.rolling(window=n2, center=False, min_periods=int(0.8*n2)).corr(delay)
        part2 = Util.array_coef(vwap_adj.iloc[-n2:,], delay.iloc[-n2:,])
        alpha = part1 + part2
        alpha[~np.isfinite(alpha)] = np.nan
        return alpha

        # close_ma = close_adj.rolling(window=n, center=False, min_periods=int(0.8*n)).mean()
        # part1 = (close_ma - close_adj)/close_ma
        # delay = close_adj.shift(n1)
        # part2 = vwap_adj.rolling(window=n2, center=False, min_periods=int(0.8*n2)).corr(delay)
        # alpha = part1 + part2
        # alpha[~np.isfinite(alpha)] = np.nan
        # return alpha.iloc[-1,]

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        return temp_result