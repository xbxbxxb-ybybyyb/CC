from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd

class FR40d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close","FactorData.Basic_factor.adjfactor","FactorData.Basic_factor.turn"]

    lag = 40

    def calc_single(self,database):
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        close = database.depend_data['FactorData.Basic_factor.close']*adjfactor
        turn = database.depend_data['FactorData.Basic_factor.turn']
        turn_former = turn.shift(1)
        re = pd.DataFrame(close.values/close.shift(1).values-1,index=close.index,columns=close.columns)
        FR = Util.rolling_corr(turn_former,abs(re),window=self.lag)
        return -FR.iloc[-1]


