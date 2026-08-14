from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
import copy


class OpenAmt(BaseFactor):

    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.open", "FactorData.Basic_factor.amt"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 10
    reform_window = 5
    def calc_single(self, database):
        minute_data_transform(database.depend_data,operation=["drop","merge"])

        high = database.depend_data["FactorData.Basic_factor.open"]
        volume = database.depend_data["FactorData.Basic_factor.amt"]
        temp = volume.rank(axis=1, pct=True)        
        alpha = Util.array_coef(high,temp)
        alpha[~np.isfinite(alpha)] = np.nan
        return alpha

    def reform(self, temp_result):
        return -(temp_result.rolling(window=self.reform_window,min_periods=1).mean())
