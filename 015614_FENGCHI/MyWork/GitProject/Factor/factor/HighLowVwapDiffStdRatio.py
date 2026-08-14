# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class HighLowVwapDiffStdRatio(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.high_minute",
    "FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.low_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag  = 0
    # fix_times=["1300"]
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteVolume= database.depend_data['FactorData.Basic_factor.volume_minute']
        
        factor = self.minute_help( MinuteHigh, MinuteLow, MinuteTurnover, MinuteVolume)
        return factor

    def minute_help(self, MinuteHigh, MinuteLow, MinuteTurnover, MinuteVolume):
        vwap = MinuteTurnover.cumsum() / MinuteVolume.cumsum()  # 滚动平均vwap
        high = MinuteHigh.rolling(window=len(MinuteHigh), min_periods=1).mean()  # 滚动平均High
        low = MinuteLow.rolling(window=len(MinuteLow), min_periods=1).mean()  # 滚动平均Low
        ratio = (vwap - low).std() / (high - vwap).std()
        return ratio

