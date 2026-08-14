# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
import time

class DuoKongPV(BaseFactor):

    factor_type = "DAY"

    depend_data = ["FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.volume_minute",
    "FactorData.Basic_factor.open_minute","FactorData.Basic_factor.close_badj",
    "FactorData.Basic_factor.turn"]
    
    lag = 1
    minute_lag = 4
    reform_window = 0

    def calc_single(self,database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteAmount = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        turn = database.depend_data['FactorData.Basic_factor.turn']

        fmt = '%Y-%m-%d'
        datelist = np.unique(MinuteAmount.index.strftime(fmt))
        weight = np.array([1+i/480 for i in range(0,240)])
        weight = weight.reshape(240,1)
        res = {}
        for date in datelist:
            dt = pd.Timestamp(date)
            Amount = MinuteAmount.loc[date]
            Volume = MinuteVolume.loc[date]
            Open = MinuteOpen.loc[date]
            vwap = Amount.values/Volume.values
            vwap[np.isinf(vwap)] = np.nan
            vwap = pd.DataFrame(vwap,index=Open.index,columns=Open.columns)
            price_open = Open.iloc[0]
            vwap.fillna(method='ffill',inplace=True)

            turn_ratio = Volume.values/Volume.sum(axis=0).values  
            vwapRolling2 = vwap.rolling(window=2,min_periods=1).mean()
            vwapRolling5 = vwap.rolling(window=5,min_periods=1).mean()
            vwapRolling10 = vwap.rolling(window=10,min_periods=1).mean()
            DuoKong = vwap.values - (vwapRolling2.values + vwapRolling5.values + vwapRolling10.values)/3
            DuoKong[abs(DuoKong)<np.nanmax(abs(DuoKong),axis=0)*0.5] = np.nan
            
            DuoKong_weight = DuoKong*weight*turn_ratio
            DuoKong_weight_sums = np.nansum(DuoKong_weight,axis=0)
            res[dt] = pd.Series(DuoKong_weight_sums,index=Open.columns)

        up_var = pd.DataFrame.from_dict(res).T
        close_adj_chg = pd.DataFrame(close_adj.values/close_adj.shift(1).values-1,index=close_adj.index,columns=close_adj.columns)
        close_adj_chg_rank = close_adj_chg.rank(pct=True,axis=1)

        turn_rate_rank = turn.rank(pct=True,axis=1)
        up_var_stat = up_var.rolling(window=5,min_periods=1).mean().iloc[-1]*(1+turn_rate_rank.iloc[-1])*close_adj_chg_rank.iloc[-1]
        up_var_stat[np.isinf(up_var_stat)] = np.nan

        return -up_var_stat