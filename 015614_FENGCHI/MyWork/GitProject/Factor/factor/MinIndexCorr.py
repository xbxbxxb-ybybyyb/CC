import time
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：MinIndexCorr
* 逻辑：该因子是主要描述的是个股和整个全A指数的净值的相关性的稳定性，长期来看如果关系越稳定越容易取得超额收益
* 因子参数：分钟数据的高开低收
* 作者：陈卓
* 日期：2019.4.25
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.22
'''


class MinIndexCorr(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.open_adj_minute",
                   "FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.close",
                   "FactorData.Basic_factor.free_float_shares"]
    lag = 10
    reform_window = 10

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        open_minute = single_database.depend_data["FactorData.Basic_factor.open_adj_minute"]
        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        close = single_database.depend_data["FactorData.Basic_factor.close"]
        free_float_shares = single_database.depend_data["FactorData.Basic_factor.free_float_shares"]
        free_float_cap = pd.DataFrame(close.values * free_float_shares.values, index=close.index,
                                      columns=close.columns)

        dailyf = self.minute(free_float_cap, close_minute, open_minute)
        ans = dailyf.iloc[-1]
        return ans

    def minute(self, ZZ500_data, MinuteClose, MinuteOpen):
        fmt = '%Y%m%d'
        date_list = np.unique(MinuteOpen.index.strftime(fmt))
        df_ratio = pd.DataFrame(index=date_list, columns=MinuteOpen.columns)
        for date in date_list:
            close = MinuteClose.loc[date]
            ffc = ZZ500_data.loc[date]
            netv = close / close.iloc[0,]

            arr1 = np.nanmean(ffc.values * netv.values / ffc.sum(), axis=1)
            arr2 = np.ones(close.shape)
            arr = arr2 * arr1.reshape(len(arr1), 1)
            df = pd.DataFrame(arr, index=close.index, columns=close.columns)
            df_ratio.loc[date] = array_coef(netv, df)
        return df_ratio

    def reform(self, temp_result):
        arr = temp_result.rolling(window=self.reform_window, min_periods=5).mean().values / \
              temp_result.rolling(window=self.reform_window, min_periods=5).std().values
        temp_result = pd.DataFrame(arr, index=temp_result.index, columns=temp_result.columns)
        return temp_result