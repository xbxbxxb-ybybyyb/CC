# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class MinuteEODSortinoRatioSharpe(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window=10
    fix_times=["1500"]     
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']

        result = self.minute_help(MinuteClose)

        return result
    def reform(self, temp_result):

        res = temp_result.rolling(window=10,min_periods=1).mean()/temp_result.rolling(window=10,min_periods=1).std()
        return res
    def minute_help(self, MinuteClose):
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))
        for date in date_list:
            close_df = MinuteClose.loc[date]
            return_df = pd.DataFrame(close_df.values/close_df.shift(1).values-1,index=close_df.index,columns=close_df.columns)
            downside_return_df = return_df[return_df < 0]
            sortino = return_df.iloc[-120:].mean() / np.nanstd(downside_return_df.iloc[-120:])
            result_df = sortino

        return -result_df