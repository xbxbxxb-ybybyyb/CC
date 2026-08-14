# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteTRtnVRatioRank(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.volume_minute"]
    lag = 0
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))

        date = date_list[-1]
        close = MinuteClose.loc[date]
        volume = MinuteVolume.loc[date].values[-30:]

        ret = (close.values/close.shift(1).values-1)
        
        volume_high_rtn = np.where(ret[-30:] > np.nanmean(ret,axis=0) + np.nanstd(ret,axis=0),volume,np.nan)
        volume_low_rtn = np.where(ret[-30:] < np.nanmean(ret,axis=0) - np.nanstd(ret,axis=0),volume,np.nan)
        
        res = -np.nanmean(volume_high_rtn,axis=0) / np.nanmean(volume_low_rtn,axis=0)
        res = pd.Series(res,index=close.columns).rank()

        return res