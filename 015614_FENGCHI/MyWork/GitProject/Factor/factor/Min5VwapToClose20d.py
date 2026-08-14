from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class Min5VwapToClose20d(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.amt_minute",
                   "FactorData.Basic_factor.is_valid",]
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
            
        close_5min = close.asfreq(freq='5min').dropna(how='all')
        volume_5min = volume.groupby(pd.Grouper(freq='5min')).sum().dropna(how ='all')
        volume_5min = volume_5min[~((volume_5min.index.hour==11) & (volume_5min.index.minute>25) | (volume_5min.index.hour ==12))]
        amt_5min = amt.groupby(pd.Grouper(freq='5min')).sum().dropna(how ='all')
        amt_5min = amt_5min[~((amt_5min.index.hour==11) & (amt_5min.index.minute>25) | (amt_5min.index.hour ==12))]   

        vwap_5min = amt_5min / volume_5min
        vwap_5min.fillna(method='ffill', inplace=True)
        vwap_to_close = vwap_5min.values / close_5min.values
        ans = np.nanmean(vwap_to_close, axis=0)     
        ans = pd.Series(ans, index=close.columns)
        ans[is_valid.iloc[-1]==0] = np.nan
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        return - temp_result.rolling(self.reform_window,min_periods=1).mean() 


        