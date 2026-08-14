from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class VolBurstReturn(BaseFactor):

    factor_type = "FIX"
    depend_data = [ 
                 "FactorData.Basic_factor.close_adj_minute",
                "FactorData.Basic_factor.volume_adj_minute",]

    lag = 5
    minute_lag = 1
    
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close_minute = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_adj_minute']

        date_list = sorted(np.unique(close_minute.index.strftime('%Y%m%d')))
        date = date_list[-1]
        pre_date = date_list[-2]
        close_minute1 = close_minute.loc[pre_date] 
        re1 = pd.DataFrame(close_minute1.values/close_minute1.shift(1).values-1,
                          index = close_minute1.index, columns =close_minute1.columns)
        close_minute2 = close_minute.loc[date] 
        re2 = pd.DataFrame(close_minute2.values/close_minute2.shift(1).values-1,
                          index = close_minute2.index, columns =close_minute2.columns)
        re = pd.concat([re1,re2])
        volma10 = volume_minute.rolling(10).mean()
        
        condi = pd.DataFrame(volume_minute.values/volma10.values > 3, index = volume_minute.index,
                            columns = volume_minute.columns)
        return -(re[condi] * volume_minute).sum()/volume_minute.sum()


    