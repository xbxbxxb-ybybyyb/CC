# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteCloseTurnCorr(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))

        date = date_list[-1]
        close = MinuteClose.loc[date]
        amt = MinuteAmt.loc[date]
        t_ma = amt.iloc[-5:].mean() / amt.iloc[-30:].mean()
        c_ma = close.iloc[-5:].mean() / close.iloc[-30:].mean()
        corr = Util.array_coef(amt.iloc[-15:],close.iloc[-15:])
        t_ma_rank = t_ma.rank(ascending=False, pct=True)
        c_ma_rank = c_ma.rank(ascending=False, pct=True)
        corr_rank = corr.rank(ascending=False, pct=True)
        alpha = t_ma_rank + c_ma_rank + corr_rank


        return alpha

