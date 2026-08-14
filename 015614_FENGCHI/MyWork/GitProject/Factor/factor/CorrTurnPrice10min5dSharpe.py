from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class CorrTurnPrice10min5dSharpe(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.open_minute",
    "FactorData.Basic_factor.high_minute","FactorData.Basic_factor.low_minute",
    "FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.float_a_shares"]
    lag = 0
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        float_a_shares = database.depend_data['FactorData.Basic_factor.float_a_shares']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))

        date = date_list[-1]
        close = MinuteClose.loc[date].iloc[-120:]
        close_mean = close.rolling(window=10,min_periods=1).mean()
        open = MinuteOpen.loc[date].iloc[-120:]
        volume = MinuteVolume.loc[date].iloc[-120:]
        high = MinuteHigh.loc[date].rolling(window=10,min_periods=1).max().iloc[-120:]
        low = MinuteLow.loc[date].rolling(window=10,min_periods=1).min().iloc[-120:]
        re = (high-low)/open.shift(10)
        turn = (volume/float_a_shares.iloc[0]).rolling(window=10,min_periods=1).mean()
        CorrTurnPrice= Util.array_coef(re*turn,close)

        return -CorrTurnPrice
    
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window,1).mean()/temp_result.rolling(self.reform_window,1).std()
    
    