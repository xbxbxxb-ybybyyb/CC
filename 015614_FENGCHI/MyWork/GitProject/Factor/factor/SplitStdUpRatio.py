import time
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：SplitStdUpRatio_13h
* 因子功能描述：当日截至13:00，位于当前价格之下的上行收益率标准差/位于当前价格之上的上行收益率标准差
  该值越大，说明价格较低时上行收益波动较大，多空博弈更剧烈，有底部支撑，价格较高时，上行收益稳定，后市易涨难跌
* 因子参数：[MinuteTurnover]: 分钟成交额
           [MinuteVolume]: 分钟成交量
           [MinuteClose]: 分钟收盘价
           [MinuteOpen]: 分钟开盘价
* 作者：周璇
* 因子创建日期：2019.9.24
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.22
'''


class SplitStdUpRatio(BaseFactor):
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

        arr = amt_minute.values / volume_minute.values
        vwap = pd.DataFrame(arr, index=volume_minute.index,
                            columns=volume_minute.columns)

        arr = vwap.values / vwap.shift(1).values - 1
        re = pd.DataFrame(arr, index=vwap.index, columns=vwap.columns)


        vwap_now = pd.DataFrame(np.array([vwap.iloc[-5:].mean()]*len(close_adj_minute)),
                                index=close_adj_minute.index,
                                columns=close_adj_minute.columns)
        mask0 = pd.DataFrame(close_adj_minute.values > open_adj_minute.values, index=close_adj_minute.index,
                             columns=close_adj_minute.columns)
        mask1 = pd.DataFrame(vwap > vwap_now, index=vwap.index, columns=vwap.columns)
        mask2 = pd.DataFrame(vwap < vwap_now, index=vwap.index, columns=vwap.columns)

        HigherUp = re[np.logical_and(mask1, mask0)].std()
        LowerUp = re[np.logical_and(mask2, mask0)].std()

        ans = pd.Series(LowerUp.values / HigherUp.values, index=HigherUp.index)
        return ans
