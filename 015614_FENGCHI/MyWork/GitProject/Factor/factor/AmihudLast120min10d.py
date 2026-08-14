from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

class AmihudLast120min10d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.amt_minute"]

    lag = 0
    reform_window = 10

    def calc_single(self,database): 
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']
        amt_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        re = close_minute.values[-1]/close_minute.values[-121]-1
        amihud = re/np.nansum(amt_minute.values[-120:],axis=0)*100000000.

        return pd.Series(-amihud,index=close_minute.columns)
    
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window,1).mean()