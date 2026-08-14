from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import copy
import time
from sklearn.preprocessing import scale

class ReCorrMean5dRank(BaseFactor):
    
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.adjfactor",
                        "FactorData.Basic_factor.close",
                    "FactorData.Basic_factor.is_valid",]

    lag = 5
    
    def calc_single(self, database):
    
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        close = database.depend_data['FactorData.Basic_factor.close']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        
        flag = pd.DataFrame(is_valid.values==1, index=is_valid.index, columns=is_valid.columns).iloc[-1]
        close_adj = close*adjfactor
        re = (close_adj-close_adj.shift(1))/close_adj.shift(1)
        re = re.reindex(columns = flag[flag].index)
        a = re.corr().stack()
        return a.groupby(level=0).mean().rank(pct=True)

    
