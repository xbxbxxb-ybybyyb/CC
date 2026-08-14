from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class MinuteliqSwingSharpe5d(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute", 
                   "FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.is_valid"]
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        low = database.depend_data['FactorData.Basic_factor.low_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']

        minute_amt_5min = amt.groupby(pd.Grouper(freq = '5min')).sum().dropna(how ='all')
        minute_amt_5min = minute_amt_5min[~((minute_amt_5min.index.hour==11) & (minute_amt_5min.index.minute>25) | (minute_amt_5min.index.hour ==12))]
        minute_close_5min = close.groupby(pd.Grouper(freq = '5min')).last().dropna(how ='all')
        minute_high_5min = high.groupby(pd.Grouper(freq = '5min')).max().dropna(how ='all')
        minute_low_5min = low.groupby(pd.Grouper(freq = '5min')).min().dropna(how ='all')
            
        swing = (minute_high_5min.values[1:] - minute_low_5min.values[1:]) / minute_close_5min.values[:-1]       
        ret = minute_close_5min.values[1:] / minute_close_5min.values[:-1] - 1.
        illiq = np.abs(ret) / minute_amt_5min.values[1:]
        zscore = (illiq - np.nanmean(illiq, axis=0)) / np.nanstd(illiq, axis=0, ddof=1)
        ans = np.nansum(swing*np.where(zscore < 2., minute_amt_5min.values[1:], np.nan), axis=0) / np.nansum(minute_amt_5min.values[1:], axis=0)
            
        ans = pd.Series(ans, index=close.columns)
        ans[is_valid.iloc[-1]==0] = np.nan
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean() / temp_result.rolling(self.reform_window).std()