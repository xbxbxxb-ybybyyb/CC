from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import pandas as pd
import numpy as np


class GTJA_007(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.vwap", "FactorData.Basic_factor.close","FactorData.Basic_factor.volume",\
    "FactorData.Basic_factor.adjfactor"]    
    lag = 4    
    def calc_single(self,database):
        close_ = database.depend_data['FactorData.Basic_factor.close']
        vwap_ = database.depend_data['FactorData.Basic_factor.vwap']
        volume_ = database.depend_data['FactorData.Basic_factor.volume']
        adjfactor_ = database.depend_data['FactorData.Basic_factor.adjfactor']
        vwap_adj = vwap_*adjfactor_
        close_adj = close_*adjfactor_
        volume_adj = volume_/adjfactor_

        n = 3
        price_diff = (vwap_adj-close_adj)/close_adj
        part1 = price_diff.rolling(window=3).max().rank(axis=1, pct=True)
        part2 = price_diff.rolling(window=3).min().rank(axis=1, pct=True)
        part3 = (volume_adj.diff(n)).rank(axis=1,pct=True)
        alpha = part1+part2*part3
        alpha[~np.isfinite(alpha)] = np.nan
        return alpha.iloc[-1]
