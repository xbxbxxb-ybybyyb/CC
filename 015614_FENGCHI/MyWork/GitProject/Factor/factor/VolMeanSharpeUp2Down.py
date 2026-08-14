from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class VolMeanSharpeUp2Down(BaseFactor):

    factor_type = "FIX"
    depend_data = [ 
                 "FactorData.Basic_factor.close_minute",
                 "FactorData.Basic_factor.volume_minute",]

    lag = 0
    minute_lag = 0
    reform_window= 10
    
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']
        c_mean = close_minute.rolling(window=5,min_periods=4).mean()
        v_mean = volume_minute.rolling(window=5,min_periods=4).mean()

        VolSharpeUp = (volume_minute[close_minute>c_mean].mean(axis=0)/volume_minute[close_minute>c_mean].std(axis=0))
        VolSharpeDown =(volume_minute[close_minute<c_mean].mean(axis=0)/volume_minute[close_minute<c_mean].std(axis=0))
        VolSharpeUp2Down = VolSharpeUp/VolSharpeDown

        return VolSharpeUp2Down
