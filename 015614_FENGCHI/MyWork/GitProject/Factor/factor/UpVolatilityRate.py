from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class UpVolatilityRate(BaseFactor):

    factor_type = "FIX"
    depend_data = [ 
                 "FactorData.Basic_factor.volume_minute",
                 "FactorData.Basic_factor.amt_minute",]

    lag = 1
    minute_lag = 1

    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']
        amt_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
          
        date_list = sorted(np.unique(volume_minute.index.strftime('%Y%m%d')))
        date = date_list[-1]
        pre_date = date_list[-2]
        vwap = amt_minute/volume_minute
        vwap1 = vwap.loc[pre_date]
        vwap2 = vwap.loc[date] 
        re1 = pd.DataFrame(vwap1.values/vwap1.shift(1).values-1, index=vwap1.index,columns=vwap1.columns)
        re2 = pd.DataFrame(vwap2.values/vwap2.shift(1).values-1, index=vwap2.index,columns=vwap2.columns)

        re = pd.concat([re1,re2])
        condi= pd.DataFrame(re.values>0, index = re.index, columns=re.columns)
        result =  -re[condi].std()/re.std()
        return result