# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteCloseResist(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute",
    "FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))

        date = date_list[-1]
        Amt = MinuteAmt.loc[date]
        Close = MinuteClose.loc[date]
        Volume = MinuteVolume.loc[date]

        vwap = Amt/Volume           

        Close_chg = (Close.iloc[-1] - vwap[-30:-2].mean())/vwap[-30:-2].mean() # 基准剔除集合竞价
        Close_chg_rank = Close_chg.rank(pct=True)

        Amt_part = Amt[-2:].sum()
        Amt_ref = Amt[-30:-2].mean() # 基准剔除集合竞价
        Amt_part_chg = (Amt_part - Amt_ref)/Amt_ref
        Amt_part_chg_rank = Amt_part_chg.rank(pct=True)            

        # 计算price_up_rate
        factor = -(1+Close_chg_rank.values)*(1+Amt_part_chg_rank.values)

        res=pd.Series(factor,index=Close.columns)

        return res