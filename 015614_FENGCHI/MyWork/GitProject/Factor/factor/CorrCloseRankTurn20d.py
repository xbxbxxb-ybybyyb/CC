from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import time

class CorrCloseRankTurn20d(BaseFactor):


    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.turn","FactorData.Basic_factor.close_badj"]

    lag = 25
    reform_window = 0

    def calc_single(self,database):

        n = 20
        turn = database.depend_data['FactorData.Basic_factor.turn']
        close = database.depend_data['FactorData.Basic_factor.close_badj']
        # pctrank = lambda x: pd.Series(x).rank(pct=True).iloc[-1]
        turn_rank = turn.rolling(window=5,min_periods=1).apply(self.pctrank)
        cor = Util.array_coef(turn_rank.iloc[-n:],close.iloc[-n:])

        return -cor
    
    def pctrank(self,x):
        n = len(x)
        temp = x.argsort()
        ranks = np.empty(n)
        ranks[temp] = (np.arange(n) + 1) / n
        return ranks[-1]