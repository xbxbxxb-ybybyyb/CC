from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util


class PVTTurn5d(BaseFactor):


    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_badj","FactorData.Basic_factor.turn"]

    lag = 4


    def calc_single(self,database):
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        turn = database.depend_data['FactorData.Basic_factor.turn']
        re = close_adj.values/close_adj.shift(1).values-1
        re_turn = np.where(turn.values>turn.shift(1).values,re*turn.values,np.nan)
        PVTTurn= pd.DataFrame(re_turn,index=turn.index,columns=turn.columns).sum()

        return -PVTTurn