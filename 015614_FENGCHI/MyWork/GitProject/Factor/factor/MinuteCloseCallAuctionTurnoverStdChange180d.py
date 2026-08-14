from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteCloseCallAuctionTurnoverStdChange180d(BaseFactor):

    actor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.a_mkt_cap"]
    lag = 0
    reform_window = 180

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        a_mkt_cap = database.depend_data['FactorData.Basic_factor.a_mkt_cap']
        
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteAmt.index.strftime(fmt))

        date = date_list[-1]
        amt = MinuteAmt.loc[date]
        MinuteTurnover_last3 = amt.between_time(start_time='14:57:00', end_time='15:00:00')
        MinuteTurnover_last3 = MinuteTurnover_last3.sum()/a_mkt_cap.iloc[0]

        return MinuteTurnover_last3
    
    
    def reform(self, temp_result):
        result = temp_result.rolling(10,1).std()/temp_result.rolling(180,1).std()
        return -result
