# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import time

class HfLast120LongTurnSkew_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.close_adj_minute"]
    lag = 1
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute'][-125:].values
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_adj_minute'][-125:]
        
        re = MinuteClose.values/MinuteClose.shift(1).values-1
        temp = pd.DataFrame(np.where(re[-120:]>0,MinuteAmt[-120:],np.nan),index=MinuteClose.index[-120:],columns=MinuteClose.columns)
        
        df_factor = -temp.skew()

        return df_factor