from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinSkew40d(BaseFactor):

    actor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 40

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))

        date = date_list[-1]
        close = MinuteClose.loc[date]
        ret = pd.DataFrame((close/close.shift(1)).values-1,index=close.index,columns=close.columns)
        skew = ret.apply(self.skewness,axis=0)
        
        return -skew

    def reform(self, temp_result):
        result = temp_result.rolling(self.reform_window,int(self.reform_window*0.5)).mean()
        return result
    
    
    def skewness(self,data):
        var = np.nansum(data**2)
        sum3 = np.nansum(data**3)
        skew = np.sqrt(np.where(~np.isnan(data))[0].shape[0])*sum3/(var**1.5)
        return skew
