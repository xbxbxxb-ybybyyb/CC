# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class HighFreqVHFCorrBias(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    minute_lag = 0
    reform_window=5
    # fix_times=["1300"]
  
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']       
        factor = self.minute_help( MinuteClose)
        return factor
    def reform(self,temp_result):
        factor = temp_result
        n = 5
        res = -(factor-factor.rolling(window=n).mean())/factor.rolling(window=n).mean()
        return res


    def minute_help(self, MinuteClose):
        close = MinuteClose
        n = 5
        high = close.rolling(window=n).max()
        low = close.rolling(window=n).min()               
        ret_abs = abs(pd.DataFrame(close.values/close.shift(1).values-1,index=close.index,columns=close.columns))
        diff = ret_abs.rolling(window=n).sum()
        
        corr = Util.array_coef(high - low,diff)
        
        return corr