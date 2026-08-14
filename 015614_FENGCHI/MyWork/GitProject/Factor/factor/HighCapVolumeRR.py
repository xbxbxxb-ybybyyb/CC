from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
import copy

class HighCapVolumeRR(BaseFactor):

    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.high", "FactorData.Basic_factor.amt","FactorData.Basic_factor.free_float_shares"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 10
    reform_window=10
    def calc_single(self, database):
        minute_data_transform(database.depend_data,operation=["drop","merge"])

        high = database.depend_data["FactorData.Basic_factor.high"]
        volume = database.depend_data["FactorData.Basic_factor.amt"]
        free_float_shares = database.depend_data["FactorData.Basic_factor.free_float_shares"]
        cap = free_float_shares*high
        cap_rank = cap.rank(axis=1, pct=True)  
        temp = volume.rank(axis=1, pct=True)  

        alpha = Util.array_coef(cap_rank,temp)
        alpha[~np.isfinite(alpha)] = np.nan
        return alpha
    def reform(self, temp_result):
        return -temp_result.rolling(self.reform_window).mean()/temp_result.rolling(self.reform_window).std()
        
       

