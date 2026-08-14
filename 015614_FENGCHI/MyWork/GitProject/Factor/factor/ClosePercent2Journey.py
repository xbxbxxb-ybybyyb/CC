from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class ClosePercent2Journey(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.high_minute",
                   "FactorData.Basic_factor.low_minute",  "FactorData.Basic_factor.high", 
                   "FactorData.Basic_factor.low", "FactorData.Basic_factor.is_valid", ]    
    lag = 0
    minute_lag = 0

    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']
        low_minute = database.depend_data['FactorData.Basic_factor.low_minute']
        high_minute = database.depend_data['FactorData.Basic_factor.high_minute']
        low = database.depend_data['FactorData.Basic_factor.low']
        high = database.depend_data['FactorData.Basic_factor.high']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        ClosePercent = close_minute.rank(pct=True).iloc[-1]
        Journey = (high_minute-low_minute).sum(axis=0)
        result = -ClosePercent/(Journey/(high.iloc[-1]-low.iloc[-1]))
        return result[is_valid.iloc[-1].values==1]
