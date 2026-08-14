import time
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 迁移作者：015625
* 迁移日期：2020.1.22
'''


class SplitVolumeStdDownRatio(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.open_adj_minute",
                   "FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.volume_minute",
                   "FactorData.Basic_factor.amt_minute"]
    lag = 0

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        open_adj_minute = single_database.depend_data["FactorData.Basic_factor.open_adj_minute"]
        close_adj_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_minute"]
        amt_minute = single_database.depend_data["FactorData.Basic_factor.amt_minute"]

        vwap = pd.DataFrame(amt_minute.values / volume_minute.values, index=volume_minute.index,
                            columns=volume_minute.columns)

        volume_minute.iloc[0] = np.nan
        vwap_now = pd.DataFrame(np.array([vwap.iloc[-5:].mean()]*len(close_adj_minute)),
                                index=close_adj_minute.index,
                                columns=close_adj_minute.columns)

        mask0 = pd.DataFrame(close_adj_minute.values < open_adj_minute.values, index=close_adj_minute.index,
                             columns=close_adj_minute.columns)
        mask1 = pd.DataFrame(vwap > vwap_now, index=vwap.index, columns=vwap.columns)
        mask2 = pd.DataFrame(vwap < vwap_now, index=vwap.index, columns=vwap.columns)

        HigherUp = volume_minute[np.logical_and(mask1, mask0)].std()
        LowerUp = volume_minute[np.logical_and(mask2, mask0)].std()

        ans = pd.Series(LowerUp.values / HigherUp.values, index=HigherUp.index)
        return ans
