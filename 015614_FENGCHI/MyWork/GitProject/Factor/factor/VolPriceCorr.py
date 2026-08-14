import time
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：VolPriceCorr
* 逻辑：该因子为成交量相对于自由流通股本占比与收益率的相关性
* 因子参数：成交额，自由流通市值，收盘价，is_valid_raw
* 作者：xust
* 日期：2019.01.16
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.22
'''


class VolPriceCorr(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.amt_by_yuan",
                   "FactorData.Basic_factor.free_float_shares",
                   "FactorData.Basic_factor.close",
                   "FactorData.Basic_factor.adjfactor",
                   "FactorData.Basic_factor.is_valid_raw"]
    lag = 15

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        amt_by_yuan = single_database.depend_data["FactorData.Basic_factor.amt_by_yuan"]
        free_float_shares = single_database.depend_data["FactorData.Basic_factor.free_float_shares"]
        close = single_database.depend_data["FactorData.Basic_factor.close"]
        adjfactor = single_database.depend_data["FactorData.Basic_factor.adjfactor"]
        is_valid_raw = single_database.depend_data["FactorData.Basic_factor.is_valid_raw"]

        free_float_cap = pd.DataFrame(free_float_shares.values * close.values, index=close.index,
                                      columns=close.columns)
        n = 15

        mask = pd.DataFrame(is_valid_raw.values == 1, index=is_valid_raw.index, columns=is_valid_raw.columns)

        arr = amt_by_yuan[mask].values / free_float_cap.values
        turn = pd.DataFrame(arr, index=free_float_cap.index, columns=free_float_cap.columns)
        turn_avg = turn.rolling(window=n, min_periods=1).mean()
        turn_std = turn.rolling(window=n, min_periods=1).std()
        arr = (turn.values - turn_avg.values) / turn_std.values
        turn_norm = pd.DataFrame(arr, index=turn.index, columns=turn.columns)
        turn_norm[np.isinf(turn_norm)] = np.nan
        turn_norm_f1 = turn_norm.shift(1)

        arr = close[mask].values * adjfactor.values
        price = pd.DataFrame(arr, index=close.index, columns=close.columns)
        price_avg = price.rolling(window=n, min_periods=1).mean()
        price_std = price.rolling(window=n, min_periods=1).std()
        arr = (price.values - price_avg.values) / price_std.values
        price_norm = pd.DataFrame(arr, index=price.index, columns=price.columns)
        price_norm[np.isinf(price_norm)] = np.nan

        arr = price.values / price.shift(1).values - 1
        ret = pd.DataFrame(arr, index=price.index, columns=price.columns)
        ret_avg = ret.rolling(window=n, min_periods=1).mean()
        ret_std = ret.rolling(window=n, min_periods=1).std()
        arr = (ret.values - ret_avg.values) / ret_std.values
        ret_norm = pd.DataFrame(arr, index=ret.index, columns=ret.columns)
        ret_norm[np.isinf(ret_norm)] = np.nan
        ret_norm = ret_norm.abs()

        flyer = - rolling_corr(price_norm, turn_norm, n)
        runner = - rolling_corr(ret_norm, turn_norm_f1, n)

        flyer_norm = flyer.subtract(flyer.min(axis=1), axis=0).divide(flyer.max(axis=1)-flyer.min(axis=1), axis=0)
        runner_norm = runner.subtract(runner.min(axis=1), axis=0).divide(runner.max(axis=1)-runner.min(axis=1), axis=0)

        arr = (flyer_norm.values + runner_norm.values) / 2
        ans = pd.DataFrame(arr, index=flyer_norm.index, columns=flyer_norm.columns)
        ans = ans.iloc[-1]

        return ans

