from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util


class CorrCloseTurn5d_max(BaseFactor):


    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_badj","FactorData.Basic_factor.turn","FactorData.Basic_factor.adjfactor"]

    lag = 5

    reform_window = 5

    def calc_single(self,database):
        turn = database.depend_data['FactorData.Basic_factor.turn']
        close = database.depend_data['FactorData.Basic_factor.close_badj']
        corr = Util.rolling_corr(close,turn,self.lag)
        return corr.iloc[-1]

    def reform(self,corr):
        return -corr.rolling(window=self.reform_window,min_periods=int(0.8*self.reform_window)).max()


