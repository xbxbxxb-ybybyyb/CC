# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteTurnoverStdSharpe(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 30

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteAmt.index.strftime(fmt))

        date = date_list[-1]
        amt = MinuteAmt.loc[date]
        amt = amt.resample('5T').sum()

        std_ = amt.std()
        if len(std_.dropna()) != 0:
            res = std_
        else:
            res = pd.Series(0.0,index=amt.columns)

        return res

    def reform(self, temp_result):
        return temp_result.rolling(window=self.reform_window,min_periods=1).mean()/temp_result.rolling(window=self.reform_window,min_periods=1).std()
