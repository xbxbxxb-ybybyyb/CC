from xfactor.BaseFactor import BaseFactor
import xfactor.Util as util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class TurnGain(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.amt", "FactorData.Basic_factor.volume", "FactorData.Basic_factor.close", 
                   "FactorData.Basic_factor.open", "FactorData.Basic_factor.high", "FactorData.Basic_factor.low",
                   "FactorData.Basic_factor.adjfactor", "FactorData.Basic_factor.free_turn"]

    lag = 25

    def calc_single(self, database):
        amt = database.depend_data['FactorData.Basic_factor.amt']
        volume = database.depend_data['FactorData.Basic_factor.volume']
        close = database.depend_data['FactorData.Basic_factor.close']
        open_ = database.depend_data['FactorData.Basic_factor.open']
        high = database.depend_data['FactorData.Basic_factor.high']
        low = database.depend_data['FactorData.Basic_factor.low']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        fturn = database.depend_data['FactorData.Basic_factor.free_turn']
        
        adj_c = adj * close
        re = adj_c / adj_c.shift(1) - np.ones(adj_c.shape)
        rt = (re*fturn)[re>re.shift(1)]
        rt = -rt.rolling(window=5,min_periods=1).sum()
        corr = util.array_coef(rt.shift().iloc[1:], re.iloc[1:])
        x = -(corr * rt.iloc[-1]).abs()
        return x
