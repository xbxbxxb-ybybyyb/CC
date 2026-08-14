# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteCloseSmartGame(BaseFactor):

    """

    *因子名 : MinuteCloseSmartGame
    *因子功能描述 : 统计尾盘多空激烈博弈处（里用非流动性指标筛选）买卖力量（成交量）的博弈情况，卖方力量越强，第二天上涨概率越大。
    *因子参数 : *
    *函数返回值 : MinuteCloseSmartGame
    *作者 : 孙海平
    *因子创建日期 : 2019.4.16
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改
    *版本 : 1.0
    *历史版本 : 无

    """    
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 5


    def filterMean(self,x):    
        x_md = x.median()
        x[x<x_md] = np.nan
        return x

    def BuySellRatio(self,Volume,Ret):
        Volume_f = Volume.apply(self.filterMean)
        illiq = abs(Ret)/Volume_f
        illiq[np.isinf(illiq)] = np.nan
        illiq_f = -((-illiq).apply(self.filterMean))
        
        arr = Ret.values>0
        df1 = pd.DataFrame(arr,index=Ret.index,columns=Ret.columns)
        arr = Ret.values<0
        df2 = pd.DataFrame(arr,index=Ret.index,columns=Ret.columns)

        Buy = Volume_f[df1].sum(axis=0)
        Sell = Volume_f[df2].sum(axis=0)
        ratio = Sell/Buy    
        return ratio
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']

        fmt = '%Y-%m-%d'
        date = np.unique(MinuteClose.index.strftime(fmt))[0]
        df_skew = pd.DataFrame(index=[pd.Timestamp(date)],columns=MinuteClose.columns)


        Close = MinuteClose.loc[date]
        Volume = MinuteVolume.loc[date]

        arr = Close.values/Close.shift(1).values-1
        Ret = pd.DataFrame(arr,index=Close.index,columns=Close.columns)
        
        ratio = self.BuySellRatio(Volume.iloc[-60:,],Ret.iloc[-60:,])
      
        return ratio

    def reform(self, df_skew1):
        # 计算n日波动率
        factor = df_skew1.rolling(window=self.reform_window,min_periods=1).mean() 
        return factor 

    
