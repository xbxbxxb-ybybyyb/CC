import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor

class RSI(BaseFactor):
    depend_data = ["FactorData.Basic_factor.close", "FactorData.Basic_factor.adjfactor"]
    lag = 30

    def calc_single(self, database):
        close = database.depend_data['FactorData.Basic_factor.close']
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        # is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        # stk_code = close.columns
        # close, adjfactor = close.values, adjfactor.values
        close_adj = close * adjfactor
        
        # diff = close_adj.values[-self.lag:] - close_adj.values[-self.lag-1:-1]
        diff = close_adj.diff().values

        up = np.where(diff > 0, diff, 0)[-self.lag:]
        down = np.where(diff < 0, diff, 0)[-self.lag:]
        
        rsi = (np.nanmean(up, axis=0) + 0.01) / (np.nanmean(down, axis=0) - 0.01)
        alpha = pd.Series(rsi, index=close.columns)
        return alpha
