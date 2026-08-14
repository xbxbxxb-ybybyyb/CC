# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteReturnDiffStdSharpe(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 50

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))

        date = date_list[-1]
        close = MinuteClose.loc[date]
        close = close.resample('5T').last()
        ret = pd.DataFrame(close.values/close.shift(1).values-1,index=close.index,columns=close.columns)
        return_diff = ret.diff(1)
        res = ret.std()
        return res

    def reform(self, temp_result):
        return temp_result.rolling(window=self.reform_window,min_periods=1).mean()/temp_result.rolling(window=self.reform_window,min_periods=1).std()
       