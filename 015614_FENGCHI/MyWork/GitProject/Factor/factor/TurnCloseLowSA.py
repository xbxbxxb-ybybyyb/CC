from xfactor.BaseFactor import BaseFactor
import xfactor.Util as util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class TurnCloseLowSA(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close", "FactorData.Basic_factor.high", "FactorData.Basic_factor.low", 
                   "FactorData.Basic_factor.adjfactor", "FactorData.Basic_factor.free_turn"]

    lag = 5
    reform_window = 10

    def calc_single(self, database):
        close = database.depend_data['FactorData.Basic_factor.close']
        low = database.depend_data['FactorData.Basic_factor.low']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        fturn = database.depend_data['FactorData.Basic_factor.free_turn']
        
        adj_c = adj * close
        adj_l = adj * low
        d = adj_c / adj_l - np.ones(adj_c.shape)
        p = d.iloc[-5:].mean()
        p = np.exp(p)
        q = fturn.iloc[-5:].mean()
        x = q * p
        return x
        
    def reform(self, temp):
        return temp.rolling(window=self.reform_window, min_periods=1).mean() / temp.rolling(window=self.reform_window, min_periods=1).std()
