from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class TurnStd(BaseFactor):

    factor_type = "FIX"
    depend_data = [ 
                 "FactorData.Basic_factor.mkt_cap_ard",
                 "FactorData.Basic_factor.amt_minute",]

    lag = 1
    minute_lag = 1
    reform_window= 30
    
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        mkt_cap_ard = database.depend_data['FactorData.Basic_factor.mkt_cap_ard']
        amt_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
        fmt = '%Y%m%d'
        date_list = sorted(np.unique(amt_minute.index.strftime(fmt)))
        compute_date = date_list[-1]
        pre_date = date_list[-2]
        turnover = amt_minute.loc[compute_date][-60:]
        result = -turnover.sum() / mkt_cap_ard.loc[pre_date]

        return result
    
    def reform(self, temp_result):
        return -temp_result.rolling(window=self.reform_window, min_periods=2).std()


    