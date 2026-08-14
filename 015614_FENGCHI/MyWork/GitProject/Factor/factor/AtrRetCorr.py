import time
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 因子名 : AtrRetCorr
* 因子功能描述 : 收益率与的相关系数十日夏普
* 作者 : 肖倩
* 因子创建日期 : 2019.02.15
* 函数修改日期 : 尚未修改
* 修改人 ：尚未修改
* 修改原因 :  尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.22
'''


class AtrRetCorr(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.high_badj",
                   "FactorData.Basic_factor.low_badj",
                   "FactorData.Basic_factor.close_badj",
                   "FactorData.Basic_factor.adjfactor",
                   "FactorData.Basic_factor.pre_close",
                   "FactorData.Basic_factor.is_valid"
                   ]
    lag = 30

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        high_badj = single_database.depend_data["FactorData.Basic_factor.high_badj"]
        low_badj = single_database.depend_data["FactorData.Basic_factor.low_badj"]
        close_badj = single_database.depend_data["FactorData.Basic_factor.close_badj"]
        adjfactor = single_database.depend_data["FactorData.Basic_factor.adjfactor"]
        pre_close = single_database.depend_data["FactorData.Basic_factor.pre_close"]
        is_valid = single_database.depend_data["FactorData.Basic_factor.is_valid"]

        mask1 = pd.DataFrame(is_valid.values == 1, index=is_valid.index, columns=is_valid.columns)
        mask0 = pd.DataFrame(is_valid.values == 0, index=is_valid.index, columns=is_valid.columns)

        high_badj_valid = high_badj[mask1]
        low_badj_valid = low_badj[mask1]
        pre_close_badj = pd.DataFrame(pre_close.values * adjfactor.values, index=pre_close.index,
                                      columns=pre_close.columns)
        pre_close_badj_valid = pre_close_badj[mask1]

        # 并行化每只股票的数据
        high_low_diff = pd.DataFrame(high_badj_valid.values - low_badj_valid.values, index=close_badj.index,
                                     columns=close_badj.columns)
        pre_high_diff = pd.DataFrame(pre_close_badj_valid.values - high_badj_valid.values, index=close_badj.index,
                                     columns=close_badj.columns)
        pre_low_diff = pd.DataFrame(pre_close_badj_valid.values - low_badj_valid.values, index=close_badj.index,
                                     columns=close_badj.columns)

        df = pd.concat([high_low_diff, pre_high_diff, pre_low_diff], axis=1)

        l1 = high_low_diff.columns.tolist() * 3
        l2 = ['highlow'] * high_low_diff.shape[1] + ['prehigh'] * high_low_diff.shape[1] + \
             ['prelow'] * high_low_diff.shape[1]
        columns = pd.MultiIndex.from_arrays([l1, l2], names=('level1', 'level2'))

        df.columns = columns
        tr = df.max(axis=1, level='level1')
        df_atr = tr.rolling(window=10, min_periods=int(0.8 * 10)).mean()

        df_atr[~np.isfinite(df_atr)] = np.nan
        df_atr.columns = high_badj_valid.columns

        arr = close_badj.values / close_badj.shift(1).values - 1
        ret = pd.DataFrame(arr, index=close_badj.index, columns=close_badj.columns)
        sppi_shift = df_atr.shift(1)

        factor = rolling_corr(ret, sppi_shift, 10)
        factor = factor.rolling(10, min_periods=1).mean() / factor.rolling(10).std()
        factor[mask0] = np.nan

        ans = factor.iloc[-1, :]
        return ans










