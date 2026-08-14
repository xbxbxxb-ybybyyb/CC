# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import time


class HF_UpRetTurnDiffSharpe(BaseFactor):
    """
    * 因子名：HF_UpRetTurnDiffSharpe_13h
    * 因子功能描述：T-1日到T日滚动Vwap收益率上行时刻的时间加权换手率变化率的夏普率，代表收益率上行时刻换手率变化的稳定程度。
    * 因子参数：MinuteVolume, MinuteTurnover, free_float_cap
    * 作者：游加平
    * 因子创建日期： 2019.10.15
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.free_float_shares", 
    "FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.close"]
    lag = 2
    minute_lag = 2

    # def definition(self, MinuteVolume, MinuteTurnover, free_float_cap):
    #     factor = self.minute_help(self.minute,'MinuteValidHelp', MinuteVolume, MinuteTurnover, free_float_cap)
    #     return factor

    # def minute(self, MinuteVolume, MinuteTurnover, free_float_cap):
    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
    #     compute_date = date_list[-1]
    #     pre_date = date_list[-2]
    #     ppre_date = date_list[-3]
                
    #     volume_yes = MinuteVolume.loc[pre_date]
    #     amt_yes = MinuteTurnover.loc[pre_date]
    #     turn_yes = amt_yes / free_float_cap.loc[ppre_date]        
    #     volume_today = MinuteVolume.loc[compute_date]        
    #     amt_today = MinuteTurnover.loc[compute_date]       
    #     turn_today = amt_today / free_float_cap.loc[pre_date]        
    #     turn = turn_yes.append(turn_today)

    #     volume = volume_yes.append(volume_today)
    #     amt = amt_yes.append(amt_today)
    #     volume = volume.replace(0.,np.nan)        
    #     ret = ( amt.cumsum() / volume.cumsum() ).pct_change() 

    #     turn_diff = self.rolling_mean(turn,window=10).diff().abs()
    #     weight = np.arange(1,turn.shape[0]+1)
    #     turn_diff = turn_diff.multiply(weight,axis=0)

    #     cond = ret > self.rolling_mean(ret,window=10) 
    #     sharpe = turn_diff[cond].mean() / turn_diff[cond].std()
    #     return sharpe
    
    def rolling_mean(self,factor,window):
        return factor.rolling(window=window,min_periods=1).mean()


    def calc_single(self, database):
        MinuteTurnover = database.depend_data["FactorData.Basic_factor.amt_minute"]
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        free_float_shares = database.depend_data["FactorData.Basic_factor.free_float_shares"]
        close = database.depend_data["FactorData.Basic_factor.close"]
        free_float_cap = pd.DataFrame((free_float_shares*close ).values*10, 
            index=close.index,columns=close.columns)
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        fmt = '%Y%m%d'
        date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        compute_date = date_list[-1]
        pre_date = date_list[-2]
        ppre_date = date_list[-3]

        volume_yes = MinuteVolume.loc[pre_date]
        amt_yes = MinuteTurnover.loc[pre_date]
        # turn_yes = amt_yes / free_float_cap.loc[ppre_date] 
        free_float_cap = free_float_cap.reindex(columns=amt_yes.columns).loc[ppre_date].values
        turn_yes = pd.DataFrame(np.divide(amt_yes.values, free_float_cap),
                index=amt_yes.index, columns=amt_yes.columns )
        volume_today = MinuteVolume.loc[compute_date]        
        amt_today = MinuteTurnover.loc[compute_date]       
        # turn_today = amt_today / free_float_cap.loc[pre_date] 

        turn_today = pd.DataFrame(np.divide(amt_today.values, free_float_cap),
            index=amt_today.index, columns=amt_today.columns )

        turn = turn_yes.append(turn_today)
        volume = volume_yes.append(volume_today)
        amt = amt_yes.append(amt_today)
        volume = volume.replace(0.,np.nan)        
        # ret = ( amt.cumsum() / volume.cumsum() ).pct_change() 
        ret = amt.cumsum()/volume.cumsum()
        ret = (ret - ret.shift(1))/ret

        turn_diff = self.rolling_mean(turn,window=10).diff().abs()
        weight = np.arange(1,turn.shape[0]+1)
        turn_diff = turn_diff.multiply(weight,axis=0)
        cond = ret > self.rolling_mean(ret,window=10) 
        sharpe = turn_diff[cond].mean() / turn_diff[cond].std()
        return sharpe

