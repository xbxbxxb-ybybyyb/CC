import time
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 因子名 :RetTurnCorr
* 因子功能描述 : 去除极端值的收益率与前一日换手率的相关系数，
                 
* 因子参数 : close_adj-调整收盘价，turn-换手率，is_valid_raw-是否合法
* 作者 : 肖倩
* 因子创建日期 : 2019.6.23
* 函数修改日期 : 尚未修改
* 修改人 ：尚未修改
* 修改原因 :  尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.22
'''


class RetTurnCorr(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.close_badj",
                   "FactorData.Basic_factor.turn",
                   "FactorData.Basic_factor.is_valid_raw"]
    lag = 5

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close_adj = single_database.depend_data["FactorData.Basic_factor.close_badj"]
        amt = single_database.depend_data["FactorData.Basic_factor.turn"]
        is_valid_raw = single_database.depend_data["FactorData.Basic_factor.is_valid_raw"]

        n = 5

        arr = close_adj.values / close_adj.shift(1).values
        ret = pd.DataFrame(arr, index=close_adj.index, columns=close_adj.columns)

        ret_rank = ret.rank(pct=True, axis=1)
        turn_shift = amt.shift(1)

        mask = pd.DataFrame(ret_rank.values < 0.9, index=ret_rank.index, columns=ret_rank.columns)
        fr_cut = rolling_corr(ret[mask], turn_shift, n)

        mask = pd.DataFrame(is_valid_raw.values == 0, index=is_valid_raw.index,
                            columns=is_valid_raw.columns)
        fr_cut[mask] = np.nan

        ans = fr_cut.iloc[-1]
        return ans
