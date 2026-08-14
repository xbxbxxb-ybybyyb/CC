# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import time

class MinuteCloseUpVar(BaseFactor):


    """

    *因子名 : MinuteCloseUpVar
    *因子功能描述 : 计算分钟级高频数据因子，价格上行波动率占比
    *因子参数 : path-分钟级数据路径  adjfactor-价格复权因子
    *函数返回值 : 价格上行波动率占比因子
    *作者 : 孙海平
    *因子创建日期 : 2018.12.3
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改
    *版本 : 1.0
    *历史版本 : 无

    """
    factor_type = "DAY"
    # fix_times = ["1500"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.amt_minute",
                "FactorData.Basic_factor.open_minute"]
    lag = 0
    reform_window = 5
    # def definition(self,MinuteTurnover,MinuteVolume,MinuteOpen):

    #     up_var = self.minute_help(self.minute,'MinuteAmPmDiffHelp',MinuteTurnover,MinuteVolume,MinuteOpen)
    #     up_var_stat = -up_var.rolling(window=5,min_periods=1).mean()
    #     return up_var_stat
    
    # def minute(self,MinuteTurnover,MinuteVolume,MinuteOpen): 
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteTurnover.index.strftime(fmt))
    #     df_skew = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list],columns=MinuteTurnover.columns)

    #     for date in date_list:
    #         turnover = MinuteTurnover.loc[date]
    #         volume = MinuteVolume.loc[date]
    #         Open = MinuteOpen.loc[date]
    #         vwap = turnover/volume
    #         price_open = Open.iloc[0]

    #         vwap[vwap.gt(price_open*1.2,axis=1) & ~vwap.gt(price_open*0.8,axis=1)] = np.nan
    #         vwap.fillna(method='ffill',inplace=True)   

    #         vwap_part = vwap[-60:]
    #         vwap_mean = vwap_part.rolling(window=5).mean()
    #         chg_rate = (vwap_part-vwap_mean)/vwap_mean
    #         # 计算price_up_rate
    #         up_rate = np.array(chg_rate[chg_rate>0].var())/np.array(chg_rate.var())   

    #         df_skew.loc[date]=up_rate       
    #     return df_skew



    def calc_single(self, database):
        MinuteTurnover = database.depend_data["FactorData.Basic_factor.amt_minute"]
        MinuteOpen = database.depend_data["FactorData.Basic_factor.open_minute"]
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteTurnover.index.strftime(fmt))
        # df_skew = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list],columns=MinuteTurnover.columns)
        
        for date in date_list:
            turnover = MinuteTurnover#.loc[date]
            volume = MinuteVolume#.loc[date]
            Open = MinuteOpen#.loc[date]
            vwap = turnover/volume
            price_open = Open.iloc[0] # series

            # vwap[vwap.gt(price_open*1.2,axis=1) & ~vwap.gt(price_open*0.8,axis=1)] = np.nan
            vwap[pd.DataFrame((vwap.values - [price_open*1.2 for i in range(vwap.shape[0])])>0, 
                index=vwap.index,columns=vwap.columns)] = np.nan
            vwap[pd.DataFrame((vwap.values - [price_open*0.8 for i in range(vwap.shape[0])])<0, 
                index=vwap.index,columns=vwap.columns)] = np.nan
            vwap.fillna(method='ffill',inplace=True)   

            vwap_part = vwap[-60:]
            vwap_mean = vwap_part.rolling(window=5).mean()
            chg_rate = (vwap_part-vwap_mean)/vwap_mean
            # 计算price_up_rate
            up_rate = np.array(chg_rate[pd.DataFrame(chg_rate.values>0,index=chg_rate.index,
                columns=chg_rate.columns)].var())/np.array(chg_rate.var())   
            
            # df_skew.loc[date]=up_rate       
        return pd.Series(up_rate, index=chg_rate.columns)

    def reform(self, result):
        result = -result.rolling(window=5,min_periods=1).mean()
        return result