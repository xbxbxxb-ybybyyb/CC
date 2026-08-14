# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class FallTurnover(BaseFactor):
        # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close","FactorData.Basic_factor.adjfactor",
    "FactorData.Basic_factor.turn","FactorData.Basic_factor.is_valid_raw"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 10

    def pct_change(self,df,n,pct=False):
        df = pd.DataFrame(df.values/df.shift(n).values-1,index=df.index,columns=df.columns)
        if pct:
            df = pd.DataFrame(df.values*100,index=df.index,columns=df.columns)
        return df
    def rolling_mean(self,df ,window,min_periods=None):
        res = df.iloc[-window:,:].mean()
        if min_periods is None:
            min_periods = window
        res[df.notnull().sum()<min_periods] = np.nan
        return res
    def calc_single(self,database ):
        n = 5
        close = database.depend_data['FactorData.Basic_factor.close']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        turn = database.depend_data['FactorData.Basic_factor.turn']
        is_valid_raw = database.depend_data['FactorData.Basic_factor.is_valid_raw']
        close_adj = close*adj
        ret = self.pct_change(df=close_adj,n=1).values
        turn_ma = turn.rolling(window=n).mean().values
        factor = pd.DataFrame(ret/(1+turn_ma),index=close_adj.index,columns=close_adj.columns)
        factor[is_valid_raw.values==0] = np.nan
        factorM5= - self.rolling_mean(df=factor,window=n)

        return factorM5