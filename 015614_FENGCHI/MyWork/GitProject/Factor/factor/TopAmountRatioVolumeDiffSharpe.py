from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class TopAmountRatioVolumeDiffSharpe(BaseFactor):

    factor_type = "FIX"
    depend_data = [ 
                 "FactorData.Basic_factor.volume_minute",
                 "FactorData.Basic_factor.amt_minute",]

    lag = 5
    minute_lag = 0

    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']
        amt_minute = database.depend_data['FactorData.Basic_factor.amt_minute']

        volume_diff = volume_minute.diff()   
        amount = amt_minute.div(amt_minute.sum(axis=1), axis=0)  
        m = amount.median()
        condi = pd.DataFrame(amount.values>m.values, index = amount.index, columns=amt_minute.columns)
        return volume_diff[condi].mean() / volume_diff[condi].std()  
    