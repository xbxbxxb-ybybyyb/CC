from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform, min_forward_adj

class  MinStdW(BaseFactor):
    depend_data = ["FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 25
    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop1", "drop4"])
        minute_amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        ans = -minute_amt.std()
        return ans

    def weight(self,series,n):
        w = np.arange(1, (n + 1), 1) / n
        temp = (series * w).sum()
        return temp
    def reform(self, temp_result):
        factor_values = temp_result
        factor_values = factor_values.rolling(5, 1).mean() / factor_values.rolling(5,1).std()
        factor_values = factor_values.rank(axis=1, ascending=True)
        return -factor_values.rolling(20).apply(self.weight,args=(20,))

