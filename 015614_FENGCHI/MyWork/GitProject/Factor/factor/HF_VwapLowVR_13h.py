# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class HF_VwapLowVR_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute",
    "FactorData.Basic_factor.low_minute"]
    lag = 0
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteAmt.index.strftime(fmt))

        date = date_list[-1]
        volume = MinuteVolume.loc[date]
        amt = MinuteAmt.loc[date]
        low = MinuteLow.loc[date]

        vwap = amt / volume
        price_ratio = (vwap / low).values
        price_ratio[price_ratio==np.inf] = np.nan
        price_ratio = pd.DataFrame(price_ratio,index=amt.index,columns=amt.columns)
        
        variance_ratio = (price_ratio.rolling(5).mean()).std() / (price_ratio.rolling(10).mean()).std()

        return variance_ratio


