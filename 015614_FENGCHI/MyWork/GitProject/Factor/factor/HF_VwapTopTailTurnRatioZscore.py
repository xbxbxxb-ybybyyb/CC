# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
import time


class HF_VwapTopTailTurnRatioZscore(BaseFactor):

    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.volume_adj_minute",
                   "FactorData.Basic_factor.amt_minute",
                   "FactorData.Basic_factor.a_mkt_cap"]
    lag = 2
    reform_window = 10

    def calc_single(self, database):
        
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])

        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        a_mkt_cap = database.depend_data['FactorData.Basic_factor.a_mkt_cap'][MinuteAmt.columns]

        fmt = '%Y%m%d'
        date_list = np.unique(MinuteAmt.index.strftime(fmt))

        date = date_list[-1]
        pre_date = date_list[-2]
        ppre_date = date_list[-3]
        
        vwap = MinuteAmt.values/MinuteVolume.values
        vwap = vwap[-len(MinuteAmt.loc[date])-15:]
        turn = MinuteAmt.loc[date].values / a_mkt_cap.loc[pre_date].values
        turn_pre = MinuteAmt.loc[pre_date].values / a_mkt_cap.loc[ppre_date].values
        turn = np.append(turn_pre[-15:,:], turn, axis=0)
        turn = turn.astype(float)
        vwap = vwap.astype(float)
        turn_top = np.where(vwap > np.nanquantile(vwap,0.9,axis=0),turn,np.nan)
        turn_tail = np.where(vwap < np.nanquantile(vwap,0.1,axis=0),turn,np.nan)
        ratio = np.nanmean(turn_top,axis=0) / np.nanmean(turn_tail,axis=0)
        return pd.Series(-ratio,index=MinuteAmt.columns)

    def reform(self, temp_result):
        arr = (temp_result.values - temp_result.rolling(self.reform_window, 1).mean().values) / \
              temp_result.rolling(self.reform_window, 1).std().values
        res = pd.DataFrame(arr, index=temp_result.index, columns=temp_result.columns)
        return res
