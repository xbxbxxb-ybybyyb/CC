from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import time




class TurnoverSharpe(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.turn"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 25
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    # reform_window = 10


    def Stdev(self, DF, lag):
        stdDF = DF.rolling(window=lag).std()
        return stdDF

    def Mean(self,DF, lag):
        meanDF = DF.rolling(window=lag).mean()
        return meanDF

    def calc_single(self, database):
        amt = database.depend_data['FactorData.Basic_factor.turn']
        # result = self.Mean(amt, 100) / self.Stdev(amt, 100)
        amt = amt.iloc[-25:,]
        result = amt.mean() / amt.std()
        return result









