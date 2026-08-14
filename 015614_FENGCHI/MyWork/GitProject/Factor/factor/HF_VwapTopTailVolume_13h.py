# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import time

class HF_VwapTopTailVolume_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_adj_minute","FactorData.Basic_factor.amt_minute"]
    lag = 1
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteAmt.index.strftime(fmt))

        date = date_list[-1]
        pre_date = date_list[-2]
        volume = MinuteVolume.loc[pre_date].iloc[-60:,:].append(MinuteVolume.loc[date])
        vwap = (MinuteAmt.loc[pre_date].iloc[-60:,:].append(MinuteAmt.loc[date]) / volume).values
        vol_top = np.where(vwap>np.nanquantile(vwap,0.9,axis=0),volume,np.nan)
        vol_tail = np.where(vwap<np.nanquantile(vwap,0.1,axis=0),volume,np.nan)
        ratio = np.nansum(vol_top,axis=0) / np.nansum(vol_tail,axis=0)
        return pd.Series(-ratio,index=MinuteAmt.columns).fillna(0.)