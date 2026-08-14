from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class StdAmountDiff(BaseFactor):

    factor_type = "FIX"
    depend_data = [ "FactorData.Basic_factor.volume_minute",
                   "FactorData.Basic_factor.amt_minute",]

    lag = 0

    
    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        amt_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']
        
        vwap = (amt_minute / volume_minute)
        r= pd.DataFrame(vwap.values/vwap.shift(1).values-1, index = vwap.index, columns = vwap.columns)

        r = pd.DataFrame((r.values.T - r.mean(axis=1).values).T, index=r.index, columns=r.columns)  
        std = r.rolling(len(r), min_periods=1).std()
        std = pd.DataFrame((std.values - std.mean().values) / std.std().values, index = std.index, columns=std.columns)

        amt_minute = pd.DataFrame((amt_minute.values.T/amt_minute.sum(axis=1).values).T, index=amt_minute.index, columns=amt_minute.columns)  
        amt = amt_minute.rolling(len(amt_minute), min_periods=1).mean()   
        amt = pd.DataFrame((amt.values - amt.mean().values) / amt.std().values, index = amt.index, columns=amt.columns) 
        diff = std - amt
        a = np.arange(len(diff))
        m = pd.DataFrame((diff.values.T * a).T, index = diff.index, columns=diff.columns).sum()
        tmp = pd.DataFrame(np.square((diff.values - m.values)),index=diff.index, columns=diff.columns)
        tmp2 = pd.DataFrame((tmp.values.T*a).T, index =tmp.index, columns=tmp.columns)
        result = np.sqrt(tmp2.sum()) 
        return result
        
    