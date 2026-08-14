# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class MinuteEODSkewness120Min(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    fix_times=["1500"]      
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        result = self.minute_help(MinuteClose)
        return result

    def minute_help(self, MinuteClose):
        close_df = MinuteClose
        return_df = close_df.pct_change(periods=1)
        skew_last = return_df.iloc[-180:].skew()  # param 120, 60 for skewness
        result_df = skew_last

        return -result_df