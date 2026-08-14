from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteTWRSharpe20(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        a = database.depend_data['FactorData.Basic_factor.amt_minute']
        c = database.depend_data['FactorData.Basic_factor.close_minute']
        r = (c / c.shift()).values - 1
        return pd.Series(index=c.columns, data=-(a.iloc[-30:].values / a.iloc[-30:].sum().values * r[-30:]).mean(axis=0))

    def reform(self, temp):
        return temp.rolling(window=self.reform_window, min_periods=1).mean() / temp.rolling(window=self.reform_window, min_periods=1).std()