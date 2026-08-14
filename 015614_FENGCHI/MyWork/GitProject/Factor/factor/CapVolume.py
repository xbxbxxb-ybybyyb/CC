from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
import copy

class CapVolume(BaseFactor):

    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.low", "FactorData.Basic_factor.volume","FactorData.Basic_factor.free_float_shares"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 4
    reform_window = 40
    def calc_single(self, database):
        minute_data_transform(database.depend_data,operation=["drop","merge"])

        high = database.depend_data["FactorData.Basic_factor.low"]
        volume = database.depend_data["FactorData.Basic_factor.volume"]
        free_float_shares = database.depend_data["FactorData.Basic_factor.free_float_shares"]
        cap = free_float_shares*high
        temp = volume.rank(axis=1, pct=True)  

        alpha = Util.array_coef(cap,temp)
        alpha[~np.isfinite(alpha)] = np.nan
        return alpha
        
    def  reform(self, temp_result):
        A = -temp_result.rolling(self.reform_window).mean()
        return A        

