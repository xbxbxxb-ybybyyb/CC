from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class TurnVolatilityStd5d(BaseFactor):
    
    factor_type = "FIX"
    depend_data = [ 
                 "FactorData.Basic_factor.float_a_shares",
                 "FactorData.Basic_factor.close_adj_minute",
                 "FactorData.Basic_factor.volume_adj_minute",]

    lag = 1
    minute_lag = 1
    reform_window= 5
    
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        float_a_shares = database.depend_data['FactorData.Basic_factor.float_a_shares']
        close_minute = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_adj_minute']

        fmt = '%Y%m%d'
        date_list = sorted(np.unique(volume_minute.index.strftime(fmt)))
        pre_date = date_list[-2]
        shares = float_a_shares.loc[pre_date]
        result= (volume_minute/shares).std()
        return result
    
    def reform(self, temp_result):
        return -temp_result.rolling(window=self.reform_window, min_periods=1).std()
    


    