# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteLastHourMaxClimb20dSR(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute",
    "FactorData.Basic_factor.is_valid_raw"]
    lag = 0
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        is_valid_raw = database.depend_data['FactorData.Basic_factor.is_valid_raw']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))

        date = date_list[-1]
        close = MinuteClose.loc[date][-60:]
        min2here = close.expanding().min()
        climb2here = pd.DataFrame(close.values/min2here.values-1,index=close.index,columns=close.columns)
        factor_today = climb2here.max()
        factor_today[is_valid_raw.iloc[-1]==0] = np.nan
        return factor_today

    def reform(self, temp_result):
        return temp_result.rolling(window=self.reform_window,min_periods=1).mean()/temp_result.rolling(window=self.reform_window,min_periods=1).std()
       