from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class SmartVwapSharpe5d(BaseFactor):

    factor_type = "FIX"
    depend_data = [ "FactorData.Basic_factor.volume_minute",
                   "FactorData.Basic_factor.amt_minute",
                   "FactorData.Basic_factor.close_minute"]

    lag = 0
    reform_window = 5
    
    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        amt_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']

        MinuteVolume = volume_minute.groupby(pd.Grouper(freq = '5min')).sum().dropna(how = 'all')
        MinuteTurnover = amt_minute.groupby(pd.Grouper(freq = '5min')).sum().dropna(how = 'all')
        MinuteClose = close_minute.groupby(pd.Grouper(freq = '5min')).last().dropna(how = 'all')
        re = pd.DataFrame(MinuteClose.values/MinuteClose.shift(1).values-1, index=MinuteClose.index,columns=MinuteClose.columns)
        illiq = re.abs()/MinuteTurnover
        condi = pd.DataFrame(illiq.rank(pct=True).values>0.95,index= illiq.index, columns = illiq.columns)
        vwap = MinuteTurnover[condi].sum()/MinuteVolume[condi].sum()     
        return 1- (MinuteTurnover.sum()/MinuteVolume.sum())/vwap 

    def reform(self, temp_result):
        return temp_result.rolling(window=self.reform_window).mean()/temp_result.rolling(window=self.reform_window).std()


    