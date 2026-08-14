# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import time

class HfHalfDayCloseRtnCountDiff_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.close_adj_minute"]
    lag = 1
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = (database.depend_data['FactorData.Basic_factor.close_adj_minute'])[-240:]

        re = (MinuteClose.values/MinuteClose.shift(1).values-1)
        re_up = pd.DataFrame(np.where(re[:-120]>0,re[:-120],np.nan),index=MinuteClose.index[:-120],columns=MinuteClose.columns)
        re_down = pd.DataFrame(np.where(re[-120:]<0,re[-120:],np.nan),index=MinuteClose.index[-120:],columns=MinuteClose.columns)
        df_factor = re_up.count() - re_down.count()

        return pd.Series(df_factor,index=MinuteClose.columns)
