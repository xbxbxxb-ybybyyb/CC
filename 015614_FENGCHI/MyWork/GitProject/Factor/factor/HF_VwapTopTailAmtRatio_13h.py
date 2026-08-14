# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
import time

class HF_VwapTopTailAmtRatio_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteAmt.index.strftime(fmt))
        date = date_list[-1]
        volume = MinuteVolume.loc[date].values
        amt = MinuteAmt.loc[date].values
        vwap = amt / volume                
        amt_top = np.where(vwap > np.nanquantile(vwap,0.95,axis=0),amt,np.nan)
        amt_tail = np.where(vwap < np.nanquantile(vwap,0.05,axis=0),amt,np.nan)
        amt_top = np.nansum(amt_top,axis=0)
        amt_tail = np.nansum(amt_tail,axis=0)
        ratio = amt_top / amt_tail
        ratio[np.isinf(ratio)] = np.nan
        return pd.Series(-ratio,index=MinuteAmt.columns)
