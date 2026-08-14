from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
import time

class ReverseMomentumDouble(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.open_minute","FactorData.Basic_factor.volume_minute",
    "FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.open_minute","FactorData.Basic_factor.close_badj",
    "FactorData.Basic_factor.open_badj","FactorData.Basic_factor.high_badj","FactorData.Basic_factor.turn"]
    lag = 20
    minute_lag = 0
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteAmt = database.depend_data['FactorData.Basic_factor.amt_minute']
        columns = MinuteAmt.columns
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj'][columns]
        open_adj = database.depend_data['FactorData.Basic_factor.open_badj'][columns]
        high_adj = database.depend_data['FactorData.Basic_factor.high_badj'][columns]
        turn = database.depend_data['FactorData.Basic_factor.turn'][columns]

        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteOpen.index.strftime(fmt))
        date = date_list[-1]

        Volume = MinuteVolume.loc[date]
        Open = MinuteOpen.loc[date]
        Amt = MinuteAmt.loc[date]          

        weight = np.array([1+i/480 for i in range(0,240)])
        weight = weight.reshape(240,1)
        vwap = Amt.values/Volume.values
        vwap[np.isinf(vwap)] = np.nan
        price_open = Open.iloc[0]

        vwap = pd.DataFrame(vwap,index=Amt.index,columns=Amt.columns)
        vwap.fillna(method='ffill',inplace=True)   

        turn_ratio = Volume.values/Volume.sum(axis=0).values   

        vwapRolling2 = vwap.rolling(window=2,min_periods=1).mean()
        vwapRolling5 = vwap.rolling(window=5,min_periods=1).mean()
        vwapRolling10 = vwap.rolling(window=10,min_periods=1).mean()

        DuoKong = vwap.values - (vwapRolling2.values + vwapRolling5.values + vwapRolling10.values)/3              
        DuoKong[abs(DuoKong)<np.nanmax(abs(DuoKong),axis=0)*0.5] = np.nan            
        DuoKong_weight =DuoKong*weight
        DuoKong_weight2 = DuoKong_weight*turn_ratio
        DuoKong_weight_sums = np.nansum(DuoKong_weight2,axis=0)
        MinuteSkew = pd.Series(DuoKong_weight_sums,index=Amt.columns)


        # 价格偏离度
        close_adj_5 = close_adj.rolling(window=5,min_periods=1).mean().values
        close_adj_10 = close_adj.rolling(window=10,min_periods=1).mean().values
        reverse_price = (close_adj.values - (close_adj_5+close_adj_10)/2)/(close_adj_5+close_adj_10)/2
        reverse_price = pd.DataFrame(reverse_price,index=close_adj.index,columns=close_adj.columns)

        # 换手率偏离度
        turn_5 = turn.rolling(window=5,min_periods=1).mean().values
        turn_10 = turn.rolling(window=10,min_periods=1).mean().values
        turn_5[turn_5==0]=np.nan
        turn_10[turn_10==0]=np.nan
        reverse_turn = (turn.values - (turn_5 + turn_10)/2)/((turn_5 + turn_10)/2)
        reverse_turn = pd.DataFrame(reverse_turn,index=close_adj.index,columns=close_adj.columns)

        # 总历史偏离度
        reverse_price_rank = reverse_price.rank(pct=True,axis=1)
        reverse_turn_rank = reverse_turn.rank(pct=True,axis=1)
        reverse = reverse_price_rank*reverse_turn_rank
        reverse_ma = reverse.rolling(window=10,min_periods=1).mean()
        reverse_ma_before = reverse_ma.shift(1)
        reverse_ma_before_rank = reverse_ma_before.rank(pct=True,axis=1)

        # 动量信号
        price_chg = (high_adj.values - open_adj.values)/open_adj.values + (close_adj.values - open_adj.values)/open_adj.values
        price_chg = pd.DataFrame(price_chg,index=close_adj.index,columns=close_adj.columns)
        price_chg_rank = price_chg.rank(pct=True,axis=1)
        turn_chg = pd.DataFrame((turn.values - turn_5)/turn_5,index=close_adj.index,columns=close_adj.columns)
        turn_chg_rank = turn_chg.rank(pct=True,axis=1)
        moment_now_rank = price_chg_rank*turn_chg_rank

        MinuteSkew_rank = MinuteSkew.rank(pct=True)

        factor = 1/((1+moment_now_rank.values[-1])*(1+reverse_ma_before_rank.values[-1])*(1+MinuteSkew_rank.values))

        return pd.Series(factor,index=MinuteAmt.columns)