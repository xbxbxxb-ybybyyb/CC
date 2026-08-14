# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class HighLowHitFreqRatio(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high_minute","FactorData.Basic_factor.low_minute","FactorData.Basic_factor.adjfactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    reform_window=0
    minute_lag = 1
    lag = 2
    
    # fix_times=["1300"]
    def calc_single(self, database):
        data_min = {"FactorData.Basic_factor.high_minute":database.depend_data['FactorData.Basic_factor.high_minute'],
                   "FactorData.Basic_factor.low_minute":database.depend_data['FactorData.Basic_factor.low_minute']}
        minute_data_transform(data_min, operation = ['drop', 'merge'])
        MinuteLow = data_min['FactorData.Basic_factor.low_minute']
        MinuteHigh = data_min['FactorData.Basic_factor.high_minute']
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        factor = self.minute_help( MinuteHigh, MinuteLow, adjfactor)
        return factor
    def mul_df_series(self,df,series):
        return pd.DataFrame(df.values*series.values,index=df.index,columns=df.columns)

    def minute_help(self, MinuteHigh, MinuteLow, adjfactor):
        high = self.mul_df_series(MinuteHigh.iloc[:240],adjfactor.iloc[0] / adjfactor.iloc[1])
        low = self.mul_df_series(MinuteLow.iloc[:240],adjfactor.iloc[0] / adjfactor.iloc[1])
        MinuteHigh = (high).append(MinuteHigh.iloc[240:])
        MinuteLow = (low).append(MinuteLow.iloc[240:])
        high, low = MinuteHigh.max(), MinuteLow.min()
        ran = high - low
        thr_h, thr_l = high.values - ran.values * 0.1, low.values + ran.values * 0.1  # 振幅顶部、底部10%的价格
        return (MinuteHigh > thr_h).sum() / (MinuteLow < thr_l).sum()

