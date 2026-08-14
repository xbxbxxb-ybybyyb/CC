from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import copy
import time
from sklearn.preprocessing import scale

class VwapReCorrMean10dRank(BaseFactor):
    
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.adjfactor",
                        "FactorData.Basic_factor.volume",
                     "FactorData.Basic_factor.amt",
                    "FactorData.Basic_factor.is_valid",]

    lag = 10
    reform_window = 0
    
    def calc_single(self, database):
    
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        volume = database.depend_data['FactorData.Basic_factor.volume']
        amt = database.depend_data['FactorData.Basic_factor.amt']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        
        flag = pd.DataFrame(is_valid.values==1, index=is_valid.index, columns=is_valid.columns).iloc[-1]
        vwap = (amt/volume).fillna(method='ffill')
        vwap_adj = vwap*adjfactor
        vwap_re = (vwap_adj-vwap_adj.shift(1))/vwap_adj.shift(1)
        vwap_re = vwap_re.reindex(columns = flag[flag].index)
        a = vwap_re.corr().stack()
        return a.groupby(level=0).mean().rank(pct=True)

    