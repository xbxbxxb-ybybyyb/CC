from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class TopAmountTradingCostRatio(BaseFactor):

    factor_type = "FIX"
    depend_data = [ 
                 "FactorData.Basic_factor.volume_minute",
                 "FactorData.Basic_factor.amt_minute",]

    lag = 5
    minute_lag = 1
    reform_window = 20

    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']
        amt_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
        amt_minute = amt_minute.iloc[:240]
        volume_minute = volume_minute.iloc[:240]

        m = amt_minute.median()
        condi0 = pd.DataFrame(amt_minute.values > m.values,index=amt_minute.index, columns=amt_minute.columns)
        s = amt_minute[condi0].std()
        thr = m + s   
        condi1 = pd.DataFrame(amt_minute.values <= thr.values, index = amt_minute.index, columns = amt_minute.columns)
        condi2 = pd.DataFrame(amt_minute.values > thr.values, index = amt_minute.index, columns = amt_minute.columns)
        a = amt_minute[condi1].sum() / volume_minute[condi1].sum()
        b = amt_minute[condi2].sum() / volume_minute[condi2].sum()
        return a / b  
    
    def reform(self, temp_result):
        return temp_result.rolling(window=self.reform_window).mean() 