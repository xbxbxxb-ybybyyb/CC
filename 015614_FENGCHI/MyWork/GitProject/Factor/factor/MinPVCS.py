from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class MinPVCS(BaseFactor):  # 派生一个因子类
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.open_minute", "FactorData.Basic_factor.amt_minute"]
    reform_window = 20
    
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        open_df = database.depend_data['FactorData.Basic_factor.open_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']

        op = open_df.values[-30]
        cp = close.values[-1]
        wave30 = np.nansum(amt.values[-30:], axis=0)
        wave = np.nansum(amt.values, axis=0)
        ans = (1. - cp / op) * (wave30 / wave)
        ans = pd.Series(ans, index=close.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans
        
        

    def  reform(self, temp_result):
        A = temp_result.rolling(20,1).skew()
        return A
        
