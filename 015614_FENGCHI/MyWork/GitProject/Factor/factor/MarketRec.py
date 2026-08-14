from xfactor.BaseFactor import BaseFactor
import xfactor.Util as util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MarketRec(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close", "FactorData.Basic_factor.adjfactor", "FactorData.Basic_factor.free_turn"]

    lag = 40
    reform_window = 40

    def calc_single(self, database):
        close = database.depend_data['FactorData.Basic_factor.close']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        fturn = database.depend_data['FactorData.Basic_factor.free_turn']
        
        adj_c = adj * close
        re = adj_c / adj_c.shift(1) - np.ones(adj_c.shape)
        a = (re.iloc[-5:].mean()).values
        b = (re.iloc[-5:].std()).values
        c = (fturn.iloc[-5:].mean() / fturn.iloc[-40:].mean()).values
        a = (a - np.nanmean(a)) / np.nanstd(a)
        b = (b - np.nanmean(b)) / np.nanstd(b)
        c = (c - np.nanmean(c)) / np.nanstd(c)
        x = pd.Series(index=close.columns, data=a*b*c)
        return x
        
    def reform(self, temp):
        return -temp.rolling(window=self.reform_window, min_periods=1).std()