# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import time

class ReLow_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.low_adj_minute","FactorData.Basic_factor.open_adj_minute",
    "FactorData.Basic_factor.open_badj","FactorData.Basic_factor.close_badj","FactorData.Basic_factor.low_badj"]
    lag = 1
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_adj_minute']
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_adj_minute']
        open = database.depend_data['FactorData.Basic_factor.open_badj'][MinuteLow.columns]
        close =database.depend_data['FactorData.Basic_factor.close_badj'][MinuteLow.columns]
        low = database.depend_data['FactorData.Basic_factor.low_badj'][MinuteLow.columns]
        

        fmt = '%Y%m%d'
        date_list = np.unique(MinuteLow.index.strftime(fmt))
        date = date_list[-1]
        pre_date = date_list[-2]
        
        low_min = MinuteLow.loc[date].min(axis=0)
        open_min = MinuteOpen.loc[date].iloc[0]
                
        relow_pre = low.loc[pre_date]/open.loc[pre_date]-1
        ReLow = (low_min/close.loc[pre_date]-1)+(low_min/open_min-1)-relow_pre

        return ReLow
