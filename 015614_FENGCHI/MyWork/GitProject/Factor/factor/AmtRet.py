import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

from xfactor.FixUtil import minute_data_transform
import copy


class AmtRet(BaseFactor):

    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.close_badj",
                   "FactorData.Basic_factor.amt"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 20
    reform_window = 5
    def calc_single(self, database):
        n = 1
        minute_data_transform(database.depend_data,operation=["drop","merge"])

        close_adj = database.depend_data["FactorData.Basic_factor.close_badj"]
        amt = database.depend_data["FactorData.Basic_factor.amt"]
            
        
        re = (close_adj-close_adj.shift(n))/close_adj.shift(n)
        re_sign = re.values
        re_sign[re_sign>0] = 1
        re_sign[re_sign<0] = -1
        re_sign_ = pd.DataFrame(re_sign, index = close_adj.index, columns=close_adj.columns)        
        amt_valid = amt
        df1 = pd.DataFrame(1, index = close_adj.index, columns=close_adj.columns)
        result = (np.log((amt_valid-amt_valid.shift(n))/amt_valid.shift(n)+df1)*re_sign_).sum()
        result[np.isinf(result)] = np.nan
        return result
    def reform(self, temp_result):
        return -(temp_result.rolling(window=self.reform_window,min_periods=1).mean())/temp_result.rolling(window=self.reform_window,min_periods=1).std()
