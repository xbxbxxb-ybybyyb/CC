# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform


class AmtVolStdRankMean5d(BaseFactor):
    """

    *因子名 : AmtVolStdRankMean5d
    *因子功能描述 : 5日amt和volume的std乘积的rank
                     
    *因子参数 : amt-每日成交额，volume-成交量，is_valid_raw-是否合法
    *作者 : wulb
    *因子创建日期 : 2019.2.20
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改


    """
    factor_type = "DAY"
    # fix_times = ["1500"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.amt", "FactorData.Basic_factor.volume"]
    lag = 5

    def calc_single(self, database):
        amt = database.depend_data["FactorData.Basic_factor.amt"]
        volume = database.depend_data["FactorData.Basic_factor.volume"]
        n = 5
        # factor = amt.rolling(window=n, min_periods=n-1).std() * volume.rolling(window=n, min_periods=n-1).std()
        factor = amt.iloc[-n:].std() * volume.iloc[-n:].std()
        factor = factor.rank(pct=True)
        # factor[is_valid_raw == 0] = np.nan
        # factor = -1 * factor
        return -factor


    # def definition(self, amt, volume, is_valid_raw):
        
    #     n = 5
    #     factor = amt.rolling(window=n, min_periods=n-1).std() * volume.rolling(window=n, min_periods=n-1).std()
    #     factor = factor.rank(pct=True,axis=1)
    #     factor[is_valid_raw == 0] = np.nan
        
    #     factor = -1 * factor
    #     return factor
        
    
            
