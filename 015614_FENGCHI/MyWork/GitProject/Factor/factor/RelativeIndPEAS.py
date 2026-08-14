# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import time

class RelativeIndPEAS(BaseFactor):
    
    '''
    * 因子名：RelativeIndPEAS
    * 逻辑：相对行业PE结合全市场PE
    * 因子参数：pe，行业代码，is_valid_raw
    * 作者：xust
    * 日期：2019.01.29
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ['FactorData.Basic_factor.pe_ttm','FactorData.Basic_factor.sw_indcode1']
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 20

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        pe_ttm = database.depend_data['FactorData.Basic_factor.pe_ttm']
        industry_code_all = database.depend_data['FactorData.Basic_factor.sw_indcode1']
        industry_code_all = industry_code_all.astype(float).iloc[-1,:]
        pe = pe_ttm

        def calculate_relative_industry_avg(x, c):

            industry_list = np.unique(c.fillna(0).values).tolist()
            if 0 in industry_list:
                industry_list.remove(0)
            for i in industry_list:
                selection = pd.Series(c.values==i, index=c.index)
                x[selection] = x[selection].divide(x[selection].mean())
            return x

        # # pe = pe_ttm[is_valid_raw==1]
        pe_norm = pe.subtract(pe.min(axis=1), axis=0).divide((pe.max(axis=1)-pe.min(axis=1)), axis=0)
        pe_norm = pe_norm.iloc[-1,:]
        relative_pe = calculate_relative_industry_avg(pe.iloc[-1,:], industry_code_all)
        # relative_pe_norm = relative_pe.subtract(relative_pe.min(axis=1), axis=0).divide((relative_pe.max(axis=1)-relative_pe.min(axis=1)), axis=0)
        relative_pe_norm = (relative_pe - relative_pe.min()) / (relative_pe.max()-relative_pe.min())
        
        synthetic_pe = (relative_pe_norm + pe_norm) #/ 2
        # alpha = synthetic_pe / synthetic_pe.rolling(window=n, min_periods=n).min()
        # alpha = alpha.rolling(window=n, min_periods=n).mean() / alpha.rolling(window=n, min_periods=n).std()
        # alpha[np.isinf(alpha)] = np.nan
        # return alpha
        return synthetic_pe

    def reform(self, temp_result):
        n = 10
        alpha = temp_result / temp_result.rolling(n,min_periods=n).min()
        alpha = alpha.rolling(n, min_periods=n).mean() / alpha.rolling(n,min_periods=n).std()
        alpha[np.isinf(alpha)] = np.nan
        return alpha
