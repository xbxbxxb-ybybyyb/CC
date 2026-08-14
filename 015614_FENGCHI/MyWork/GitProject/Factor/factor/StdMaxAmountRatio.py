from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import time

class StdMaxAmountRatio(BaseFactor):

    factor_type = "FIX"
    depend_data = [ 
                "FactorData.Basic_factor.amt_minute",
                "FactorData.Basic_factor.volume_minute",]

    lag = 4
    minute_lag = 4

    
    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        amt_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']
        date_list = np.unique(amt_minute.index.strftime('%Y%m%d'))
        res = {}
        for date in date_list:
            amt = amt_minute.loc[date]
            vwap = amt_minute.loc[date]/volume_minute.loc[date]
            res[date] = self.fun(vwap, amt)
        res= pd.DataFrame(res, index = amt_minute.columns,columns = date_list).transpose()
        coef = np.e ** (np.arange(4, -1, -1) * np.log(0.5) / 2)
        result = res.mul(coef,axis=0).sum()
        return result
        
    def fun(self, vwap, turnover):
        std = vwap.resample('5min').std().dropna(how='all', axis=0)
        amount = turnover.resample('5min').sum().dropna(how='all', axis=0)
        amo_ratio = amount.div(amount.sum(axis=1), axis=0)
        con = pd.DataFrame(amo_ratio.values == amo_ratio.max().values, index= amo_ratio.index, columns=amo_ratio.columns)
        if len(con) > 0:
            return -std[con].mean() / std.mean()
        else:
            return pd.Series(np.nan, index=vwap.columns)
    