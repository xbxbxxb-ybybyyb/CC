import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

from xfactor.FixUtil import minute_data_transform


class GTJA_032(BaseFactor):

    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.volume", "FactorData.Basic_factor.high"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 3
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data,operation=["drop","merge"])

        volume = database.depend_data["FactorData.Basic_factor.volume"]
        high = database.depend_data["FactorData.Basic_factor.high"]

        n = 3
        temp1 = high.rank(axis=1,pct=True)
        temp1 = temp1.rolling(window=n).sum()
        temp1.fillna(0,inplace=True)
        
        temp2 = volume.rank(axis=1,pct=True)
        temp2 = temp1.rolling(window=n).sum()
        temp2.fillna(0,inplace=True)
        
        temp3 = Util.array_coef(temp1,temp2)
        
        temp3 = np.minimum(temp3, 1)
        temp3 = np.maximum(temp3, -1)
        # temp3[~np.isfinite(-temp3)] = np.nan        
        return temp3

    def reform(self, temp_result):
        return temp_result.rolling(window=self.reform_window).mean() / temp_result.rolling(window=self.reform_window).std()