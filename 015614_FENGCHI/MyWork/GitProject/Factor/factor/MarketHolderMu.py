from xfactor.BaseFactor import BaseFactor
import xfactor.Util as util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MarketHolderMu(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close", "FactorData.Basic_factor.adjfactor", "FactorData.Basic_factor.free_turn"]

    lag = 100
    reform_window = 5

    def calc_single(self, database):
        close = database.depend_data['FactorData.Basic_factor.close']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        fturn = database.depend_data['FactorData.Basic_factor.free_turn']
        
        adj_c = adj * close
        re = adj_c / adj_c.shift(1) - np.ones(adj_c.shape)
        a = re.iloc[-10:].mean()
        b = re.iloc[-10:].std()
        c = fturn.iloc[-10:].mean() / fturn.iloc[-100:].mean()
        x = a.rank(pct=True) + b.rank(pct=True) + c.rank(pct=True)
        return x
        
    def reform(self, temp):
        return -temp.ewm(span=2).mean()