
# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd

class CorrDownVolumeSharpe(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_badj", "FactorData.Basic_factor.high_badj",
    "FactorData.Basic_factor.volume","FactorData.Basic_factor.low_badj"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 50

    def Ts_Max(self, DF, lag):
        tsmaxDF = DF.rolling(lag,1).max()
        return tsmaxDF

    def Ts_Min(self, DF, lag):
        tsminDF = DF.rolling(lag,1).min()
        return tsminDF

    def Mean(self,DF, lag):
        meanDF = DF.rolling(window=lag, min_periods=1).mean()
        return meanDF

    def Stdev(self,DF, lag):
        stdDF = DF.rolling(window=lag, min_periods=1).std()
        return stdDF


    def calc_single(self, database):
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        high_adj = database.depend_data['FactorData.Basic_factor.high_badj']
        low_adj = database.depend_data['FactorData.Basic_factor.low_badj']
        volume = database.depend_data['FactorData.Basic_factor.volume']
        resultDF = pd.DataFrame(np.nan, columns=close_adj.columns, index=close_adj.index)
        down = (close_adj - self.Ts_Min(low_adj, 20)) / (self.Ts_Max(high_adj, 20) - self.Ts_Min(low_adj, 20))
        n = 6

        # for i in range(n, len(resultDF)):
        #     volumedf = volume.iloc[i - n:i]
        #     downdf = down.iloc[i - n:i]
        #     # resultDF.iloc[i] = Util.array_coef(volumedf,downdf)
        #     corr = volumedf.corrwith(downdf)
        #     resultDF.iloc[i] = corr
        resultDF = Util.rolling_corr(volume,down,window=n)

        resultDF = -self.Mean(resultDF, 20) / self.Stdev(resultDF, 20)
        # resultDF = -resultDF.iloc[-20:,:].mean()/resultDF.iloc[-20:,:].std()

        return resultDF.iloc[-1,:]
