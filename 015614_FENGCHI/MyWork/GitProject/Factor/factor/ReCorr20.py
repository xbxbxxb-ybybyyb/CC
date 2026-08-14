# -*- coding: utf-8 -*-
import multiprocessing
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
class ReCorr20(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_badj","FactorData.Basic_factor.is_valid_raw"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 120
    def pct_change(self,df,n,pct=False):
        df = pd.DataFrame(df.values/df.shift(n).values-1,index=df.index,columns=df.columns)
        if pct:
            df = pd.DataFrame(df.values*100,index=df.index,columns=df.columns)
        return df
    def calc_single(self, database):
        close_adj = close = database.depend_data['FactorData.Basic_factor.close_badj']
        is_valid_raw = database.depend_data['FactorData.Basic_factor.is_valid_raw']
        date_list = close_adj.index[120:]
        re = self.pct_change(close_adj,1)
        # re = close_adj/close_adj.shift(1) - 1
        pool = multiprocessing.Pool(processes=10)
        manager = multiprocessing.Manager()

        Factor_result = manager.dict()
        res = []
        for date in date_list:
            res.append(pool.apply_async(self.helper, args=(re, date, Factor_result)))
        for i, elem in enumerate(res):
            elem.get()
        pool.close()
        pool.join()
        Factor = {}
        for date in date_list:
            Factor[date] = Factor_result[date]
        Factor_df = pd.DataFrame(Factor).T.reindex(columns=is_valid_raw.columns)
        Factor_df[is_valid_raw.loc[Factor_df.index].values == 0] = np.nan
        return Factor_df.iloc[-1,:]
    

    # Find top 10% most simily stocks to construct a equal weight portfolio, calculate stock correlation with this portfolio
    def helper(self, re, date, Factor_result):

        re_cur_valid = re[:date].iloc[-120:, :]
        X = re_cur_valid.corr()
        X = X.rank(axis =1,pct=True)
        group = pd.DataFrame((X.values!=1)&(X.values>=0.9),index=X.index,columns=X.columns)
        Y = group.apply(lambda x : (re_cur_valid[re_cur_valid.columns[x]].mean(axis=1)))
        factor_today = Util.array_coef(re_cur_valid.iloc[-20:, ],Y.iloc[-20:, ])
        # factor_today = re_cur_valid.iloc[-20:, ].corrwith(Y.iloc[-20:, ])
        Factor_result[date] = factor_today