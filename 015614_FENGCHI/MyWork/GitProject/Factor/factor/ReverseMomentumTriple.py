# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class ReverseMomentumTriple(BaseFactor):
    """

    *因子名 : ReverseMomentumTriple
    *因子功能描述 : 计算反转动量确认因子，即对已经超跌的股票捕捉起始的动量信号,辅助分钟线多空/走势趋势确认信息
    *因子参数 : path-分钟级数据路径  adjfactor-价格复权因子
    *函数返回值 : 反转动量确认因子
    *作者 : 孙海平
    *因子创建日期 : 2019.1.8
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改
    *版本 : 1.0
    *历史版本 : 无

    """    
    factor_type = 'DAY'
    s_close_adj = 'FactorData.Basic_factor.close_badj'
    s_high_adj = 'FactorData.Basic_factor.high_badj'
    s_open_adj = 'FactorData.Basic_factor.open_badj'
    s_amt = 'FactorData.Basic_factor.amt'
    # s_free_float_shares = 'FactorData.Basic_factor.free_float_shares'
    # s_close = 'FactorData.Basic_factor.close'
    s_free_turn = 'FactorData.Basic_factor.free_turn'
    s_amt_min = 'FactorData.Basic_factor.amt_minute'
    s_vol_min = 'FactorData.Basic_factor.volume_minute'
    s_open_min = 'FactorData.Basic_factor.open_minute'
    depend_data = [s_close_adj, s_high_adj, s_open_adj, s_amt, s_free_turn, s_amt_min, s_vol_min, s_open_min]
    n = 5
    lag = 20
    minute_lag = 0
    def calc_single(self, database):
        # n = 5
        data_min = {self.s_amt_min : database.depend_data[self.s_amt_min],
                    self.s_vol_min : database.depend_data[self.s_vol_min],
                    self.s_open_min: database.depend_data[self.s_open_min]}
        minute_data_transform(data_min, operation = ['drop', 'merge'])
        close_adj = database.depend_data[self.s_close_adj]
        open_adj = database.depend_data[self.s_open_adj]
        high_adj = database.depend_data[self.s_high_adj]
        free_turn = database.depend_data[self.s_free_turn]
        amt = database.depend_data[self.s_amt]
        amt_min = data_min[self.s_amt_min]
        vol_min = data_min[self.s_vol_min]
        open_min = data_min[self.s_open_min]
        # 价格偏离度
        close_adj_5 = close_adj.rolling(window=5,min_periods=1).mean().tail(self.n * 2)
        close_adj_10 = close_adj.rolling(window=10,min_periods=1).mean().tail(self.n * 2)
        reverse_price = (close_adj.tail(self.n * 2) - (close_adj_5+close_adj_10)/2)/(close_adj_5+close_adj_10)/2
        # reverse_price = pd.DataFrame(reverse_price, index = close_adj.index[-self.n*2:], columns = close_adj.columns)
        # 换手率偏离度
        # turn_rate = amt/free_float_cap
        turn_5 = free_turn.rolling(window=5,min_periods=1).mean().tail(self.n * 2)
        turn_10 = free_turn.rolling(window=5,min_periods=1).mean().tail(self.n * 2)
        reverse_turn = (free_turn.tail(self.n*2) - (turn_5 + turn_10)/2) / ((turn_5 + turn_10)/2)
        # reverse_turn = pd.DataFrame(reverse_turn, index = close_adj.index[-self.n * 2], columns=close_adj.columns)
        # 总历史偏离度
        reverse_price_rank = reverse_price.rank(pct=True,axis=1)
        reverse_turn_rank = reverse_turn.rank(pct=True,axis=1)
        reverse = reverse_price_rank*reverse_turn_rank
        reverse_ma_before = reverse.shift(1).tail(self.n * 2).mean()
        # reverse_ma_before = reverse_ma.shift(1)
        reverse_ma_before_rank = reverse_ma_before.rank(pct=True)

        # 动量信号
        price_chg = (high_adj.iloc[-1] - open_adj.iloc[-1])/open_adj.iloc[-1] + (close_adj.iloc[-1] - open_adj.iloc[-1])/open_adj.iloc[-1]
        price_chg_rank = price_chg.rank(pct=True)
        turn_rate_ma = free_turn.tail(self.n).mean()
        turn_chg = (free_turn.iloc[-1] - turn_rate_ma)/turn_rate_ma
        turn_chg_rank = turn_chg.rank(pct=True)
        moment_now_rank = price_chg_rank*turn_chg_rank

        minute_factor = self.minute(amt_min,vol_min,open_min)        

        MinuteSkew = minute_factor['Duokong']
        MinuteTrendStrength = minute_factor['Trend']

        MinuteSkew_rank = MinuteSkew.rank(pct=True)
        MinuteTrendStrength_rank = MinuteTrendStrength.rank(pct=True)

        factor = -((1+reverse_ma_before_rank)*(0.5+moment_now_rank)*(1+MinuteSkew_rank)*(1+MinuteTrendStrength_rank))
        return factor
    
    def minute(self,MinuteTurnover,MinuteVolume,MinuteOpen): 
        # fmt = '%Y-%m-%d'
        # date_list = np.unique(MinuteTurnover.index.strftime(fmt))
        minute_factor = {}
        # df_skew = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list],columns=MinuteTurnover.columns)
        # MinuteTrendStrength = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list],columns=MinuteTurnover.columns)


        weight = np.array([1+i/480 for i in range(0,240)])
        weight = weight.reshape(240,1)
        # for date in date_list:
        Turover = MinuteTurnover
        Volume = MinuteVolume
        Open = MinuteOpen
        vwap = Turover/Volume
        price_open = Open

        vwap = Turover/Volume
        vwap[vwap.gt(price_open*1.2,axis=1) & ~vwap.gt(price_open*0.8,axis=1)] = np.nan
        vwap.fillna(method='ffill',inplace=True)   
        
        turn_ratio = Volume/Volume.sum(axis=0)   

        vwapRolling5 = vwap.rolling(window=2,min_periods=1).mean()
        vwapRolling10 = vwap.rolling(window=5,min_periods=1).mean()
        vwapRolling20 = vwap.rolling(window=10,min_periods=1).mean()

        DuoKong = vwap - (vwapRolling5 + vwapRolling10 + vwapRolling20)/3              
        DuoKong[abs(DuoKong) < abs(DuoKong).max(axis=0)*0.5] = np.nan            
        DuoKong_weight = pd.DataFrame(data=DuoKong.values*weight,index=DuoKong.index,columns=DuoKong.columns) 
        DuoKong_weight2 = DuoKong_weight*turn_ratio
        DuoKong_weight_sums = DuoKong_weight2.sum(axis=0)

        price_open = Open.iloc[0]
        vwap = Turover/Volume
        vwap[vwap.gt(price_open*1.2,axis=1) & ~vwap.gt(price_open*0.8,axis=1)] = np.nan
        vwap.fillna(method='ffill',inplace=True)   
        p_corr = (vwap.iloc[-1]-vwap.iloc[0])/abs(vwap.shift(-1) - vwap).sum(axis=0)

        # MinuteTrendStrength.loc[date] = p_corr.values            
        # df_skew.loc[date] = DuoKong_weight_sums 

        MinuteTrendStrength = p_corr
        df_skew = DuoKong_weight_sums
        minute_factor['Duokong'] = df_skew
        minute_factor['Trend'] = MinuteTrendStrength
        return minute_factor



