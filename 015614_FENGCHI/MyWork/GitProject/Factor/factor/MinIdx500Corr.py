import time
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：MinIdx500Corr
* 逻辑：该因子是主要描述的是个股和中证500指数的净值的分钟级相关性，突出跟随主力带来的超额收益
* 因子参数：分钟数据的高开低收
* 作者：陈卓
* 日期：2019.5.7
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.22
'''


class MinIdx500Corr(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.open_adj_minute",
                   "FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.index_weight_zz500"]
    lag = 5
    reform_window = 2

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        open_minute = single_database.depend_data["FactorData.Basic_factor.open_adj_minute"]
        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        close_000905 = single_database.depend_data["FactorData.Basic_factor.index_weight_zz500"]

        dailyf = self.minute(close_000905, close_minute, open_minute)
        ans = dailyf.iloc[-1]
        return ans

    def minute(self, ZZ500_data, MinuteClose, MinuteOpen):
        fmt = '%Y%m%d'
        date_list = np.unique(MinuteOpen.index.strftime(fmt))
        df_ratio = pd.DataFrame(index=date_list, columns=MinuteOpen.columns)
        for date in date_list:
            close = MinuteClose.loc[date]
            weights = ZZ500_data.loc[date]
            netv = close / close.iloc[0,]

            arr1 = np.nanmean(weights.values * netv.values / weights.sum(), axis=1)
            arr2 = np.ones(close.shape)
            arr = arr2 * arr1.reshape(len(arr1), 1)
            df = pd.DataFrame(arr, index=close.index, columns=close.columns)
            df_ratio.loc[date] = array_coef(netv, df)
        return df_ratio

    def reform(self, temp_result):
        temp_result = temp_result.rolling(window=self.reform_window, min_periods=1).mean()
        return temp_result
