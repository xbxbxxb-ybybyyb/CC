from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class MinuteliqAmtRatioSharpe20d(BaseFactor):

    
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.amt_minute",
                    "FactorData.Basic_factor.is_valid", ]


    lag = 0
    reform_window = 20
    
    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']
        amt_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        valid = pd.DataFrame(is_valid.values==1, index=is_valid.index, columns=is_valid.columns)

        minute_amt_5min = amt_minute.groupby(pd.Grouper(freq = '5min')).sum().dropna(how ='all')   
        minute_close_5min = close_minute.groupby(pd.Grouper(freq = '5min')).last().dropna(how ='all')   
        re = minute_close_5min.values/minute_close_5min.shift(1).values - 1   
        re = pd.DataFrame(re, index = minute_close_5min.index, columns=minute_close_5min.columns)
        illiq = re.abs()/minute_amt_5min
        zscore = (illiq.values-illiq.mean().values)/illiq.std().values
        condi = pd.DataFrame(zscore<2, index=illiq.index, columns=illiq.columns)
        result = (minute_amt_5min[condi]).sum()/minute_amt_5min.sum()
        return result[valid.iloc[-1]]

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window, min_periods = 10).mean()/temp_result.rolling(self.reform_window, min_periods = 10).std()
    
    