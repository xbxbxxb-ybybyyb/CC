# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import time

class HF_VwapRetSkew_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_adj_minute","FactorData.Basic_factor.amt_minute"]
    lag = 1
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteAmt.index.strftime(fmt))

        date = date_list[-1]
        pre_date = date_list[-2] 
        
        amt = MinuteAmt.loc[pre_date:date]
        volume = MinuteVolume.loc[pre_date:date].values
        volume[volume==0.] = np.nan
        vwap = amt.values / volume
        cumvwap = np.nancumsum(amt.values,axis=0) / np.nancumsum(volume,axis=0)
        ret = pd.DataFrame(vwap / cumvwap - 1.,index=amt.index,columns=amt.columns)
        
        ret_skew = ret.groupby(pd.Grouper(freq='30min')).skew().dropna(axis=0,how='all')
        weight = np.arange(1,ret_skew.shape[0] + 1)
        skew = - ret_skew.multiply(weight,axis=0).sum()
        return skew

    def reform(self, temp_result):
        res = -temp_result/temp_result.rolling(window=self.reform_window,min_periods=1).min()
        res[np.isnan(res).all(axis=1)] = 0.
        return res