# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class HF_VwapAmtUpCorrInLowVolatility_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteAmt.index.strftime(fmt))

        date = date_list[-1]
        volume = MinuteVolume.loc[date]
        amt = MinuteAmt.loc[date]

        vwap = amt.values/volume.values
        
        up_vwap = pd.DataFrame(np.where(vwap>0,vwap,np.nan),index = amt.index,columns=amt.columns)
        up_amt = pd.DataFrame(np.where(amt.values>0,amt.values,np.nan),index = amt.index,columns=amt.columns)
        
        result = Util.array_coef(up_vwap,up_amt)
        if (~np.isnan(result)).sum()==0:
            result = pd.Series(0.,index=amt.columns)

        return result

    def reform(self, temp_result):
        res = temp_result/temp_result.rolling(window=self.reform_window,min_periods=1).std()

        return -res