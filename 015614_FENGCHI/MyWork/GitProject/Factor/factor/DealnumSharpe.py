# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd

class DealnumSharpe(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.dealnum"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 10
    reform_window = 15

    def Mean(self,DF, lag):
        meanDF = DF.iloc[-lag:,:].mean()
        return meanDF
    def Stdev(self,DF, lag):
        stdDF = DF.iloc[-lag:,:].std()
        return stdDF
    def calc_single(self, database):
        dealnum = database.depend_data['FactorData.Basic_factor.dealnum']
        resultDF = self.Mean(dealnum, 10) / self.Stdev(dealnum, 10)

        return resultDF
    def reform(self, up_var):
        # 计算n日波动率
        up_var = (up_var.rolling(window=self.reform_window).mean())
         
        return up_var       