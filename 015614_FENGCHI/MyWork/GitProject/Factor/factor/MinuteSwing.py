from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteSwing(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.high_minute","FactorData.Basic_factor.low_minute",
    "FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteHigh.index.strftime(fmt))

        date = date_list[-1]
        high = MinuteHigh.loc[date].values
        low = MinuteLow.loc[date].values
        volume = MinuteVolume.loc[date].values
        amt = MinuteAmt.loc[date].values

        swing = (high - low) / low
        swing[np.isinf(swing)] = 0
        swing = np.nansum(swing,axis=0)

        volume_am = volume[: 120]
        volume_pm = volume[120:]

        amt_am = amt[: 120]
        amt_pm = amt[120:]
        
        price_am = np.sum(amt_am,axis=0) / np.sum(volume_am,axis=0)
        price_pm = np.sum(amt_pm,axis=0) / np.sum(volume_pm,axis=0)
                    
        price_diff = price_pm - price_am
        sign = price_diff.copy()
        sign[price_diff > 0] = -1
        sign[price_diff == 0] = 0
        sign[price_diff < 0] = 1
        
        signed_swing = sign * swing
        signed_swing[np.isinf(signed_swing)] = np.nan
        

        return pd.Series(signed_swing,index=MinuteHigh.columns)

    def reform(self, temp_result):
        return temp_result.fillna(method='ffill').rolling(self.reform_window,1).mean()