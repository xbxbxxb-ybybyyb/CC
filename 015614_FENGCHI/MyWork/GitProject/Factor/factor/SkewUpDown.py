from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class SkewUpDown(BaseFactor):

    factor_type = "FIX"
    depend_data = [             
                   "FactorData.Basic_factor.close_adj_minute"]

    minute_lag = 2
    reform_window = 0
    
    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close_minute = database.depend_data['FactorData.Basic_factor.close_adj_minute']

        diff = close_minute.diff().rolling(20).mean()
        tmp1 = pd.DataFrame((diff.values > 0), index = diff.index, columns = diff.columns)
        tmp2 = pd.DataFrame((diff.values < 0), index = diff.index, columns = diff.columns)        
        UP = diff * tmp1
        DO = diff * tmp2
        result = -UP.skew()+DO.skew()

        return result

