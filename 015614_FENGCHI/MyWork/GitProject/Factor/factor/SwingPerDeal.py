from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class SwingPerDeal(BaseFactor):

    factor_type = "FIX"
    depend_data = [ 
                  "FactorData.Basic_factor.close_adj_minute",
                 "FactorData.Basic_factor.volume_adj_minute",
                 "FactorData.Basic_factor.open_adj_minute",
                 "FactorData.Basic_factor.dealnum",
                 "FactorData.Basic_factor.low_adj_minute",
                 "FactorData.Basic_factor.high_adj_minute"]

    lag = 5
    minute_lag = 1
    
    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close_minute = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        dealnum = database.depend_data['FactorData.Basic_factor.dealnum']
        high_minute = database.depend_data['FactorData.Basic_factor.high_adj_minute']
        low_minute = database.depend_data['FactorData.Basic_factor.low_adj_minute']
        open_minute = database.depend_data['FactorData.Basic_factor.open_adj_minute']
        

        date_list = sorted(np.unique(open_minute.index.strftime('%Y%m%d')))
        date = date_list[-1]
        pre_date = date_list[-2]
        #dealnum = dealnum.astype(np.float64)
        dealnum_yesterday = dealnum.loc[pre_date]
        
        dealnum_today = dealnum_yesterday/volume_minute.loc[pre_date].sum() * volume_minute.loc[date].sum()
                
        swing = (high_minute-low_minute)/open_minute
        swingsum = swing.sum()
        return swingsum/dealnum_today
    
    
        