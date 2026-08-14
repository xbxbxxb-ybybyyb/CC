# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd

class PEAdj(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    s_Wind = 'FactorData.WIND_AShareFinancialIndicator'
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = [s_Wind,"FactorData.Basic_factor.pe_ttm"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 10
    financial_lag = 200
    reform_window = 15

    #YOYASSETS
    #YOYNETPROFIT
    def arithmetic(self,df,scalar,method='+'):
        ## method = '+',"-",'*','/'
        if method=='+':
            return pd.DataFrame(df.values+scalar,index=df.index,columns=df.columns)
        elif method=='-':
            return pd.DataFrame(df.values-scalar,index=df.index,columns=df.columns)
        elif method=='*':
            return pd.DataFrame(df.values*scalar,index=df.index,columns=df.columns)
        elif method=='/':
            return pd.DataFrame(df.values/scalar,index=df.index,columns=df.columns)
    def rolling_mean(self,df ,window,min_periods=None):
        res = df.iloc[-window:,:].mean()
        if min_periods is None:
            min_periods = window
        res[df.notnull().sum(axis=0)<min_periods] = np.nan
        return res
    def rolling_std(self,df ,window,min_periods=None):
        res = df.iloc[-window:,:].std()
        if min_periods is None:
            min_periods = window
        res[df.notnull().sum(axis=0)<min_periods] = np.nan
    def calc_single(self, database):
        
        pe_ttm_orig = database.depend_data['FactorData.Basic_factor.pe_ttm']
        pe_ttm = pe_ttm_orig.iloc[-1]

        Wind = database.depend_data[self.s_Wind]

        eps = Wind['S_FA_PROFITTOGR']
        eps = eps.unstack().fillna(method='ffill')
        eps = eps.reindex(pe_ttm_orig.columns, axis = 1)
        profit2income = eps.iloc[-1]


        eps = Wind['S_FA_DEBTTOASSETS']
        eps = eps.unstack().fillna(method='ffill')
        eps = eps.reindex(pe_ttm_orig.columns, axis = 1)
        deb2asset = eps.iloc[-1]


        a = deb2asset/100+1
        b = profit2income/100+1
        dp = -pe_ttm*a/b
        return dp

    def reform(self, temp_result):
        return temp_result.rolling(window=self.reform_window,min_periods=1).mean()
