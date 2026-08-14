import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
from xfactor.Util import array_coef

'''
* 因子名：MinAbnCorr
* 逻辑：该因子是主要描述的是个股相比整个全A指数的净值的相关性的异常波动，相关性异常升高意味着行情的到来
* 因子参数：分钟数据的高开低收
* 作者：陈卓
* 日期：2019.4.25
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.10
'''


class MinAbnCorr(BaseFactor):
    factor_type = "DAY"
    fix_times = ["1500"]
    depend_data = ["FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.free_float_shares",
                   "FactorData.Basic_factor.close"]
    lag = 0
    reform_window = 40

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        free_float_shares = single_database.depend_data["FactorData.Basic_factor.free_float_shares"]
        close = single_database.depend_data["FactorData.Basic_factor.close"]

        # 日频
        ffc = pd.DataFrame(free_float_shares.values * close.values, index=close.index,
                           columns=close.columns)

        # 分钟频
        netv = pd.DataFrame(close_minute.values / close_minute.iloc[0,].values, index=close_minute.index,
                            columns=close_minute.columns)

        arr = ffc.values * netv.values / ffc.sum().values
        index_netv = pd.DataFrame(arr, index=netv.index, columns=netv.columns).mean(axis=1)

        arr = np.ones([netv.shape[0], netv.shape[1]]) * index_netv.values.reshape(len(index_netv), 1)
        df = pd.DataFrame(arr, index=netv.index, columns=netv.columns)

        ans = array_coef(netv, df)
        return ans

    def reform(self, temp_result):
        arr = (temp_result.values - temp_result.rolling(20, min_periods=10).mean().values) / \
                    temp_result.rolling(20, min_periods=10).std().values
        result = pd.DataFrame(arr, index=temp_result.index, columns=temp_result.columns)
        ans = result.rolling(20, min_periods=10).mean()
        return ans
