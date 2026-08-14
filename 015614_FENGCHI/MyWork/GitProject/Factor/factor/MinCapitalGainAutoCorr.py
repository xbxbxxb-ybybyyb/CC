import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：MinCapitalGainOverhang
* 因子功能描述：以换手率加权的成交均价定义参考价格，计算当前价格相对于参考价格的位置。
        股票投资者相对于参考价格的平均浮盈浮亏。投资者在投资股票时，倾向卖出盈利的股票、继续持有亏损的股票
* 因子参数：  MinuteClose,MinuteHigh, MinuteLow
* 作者： 肖倩
* 因子创建日期： 2019.7.8
* 函数修改日期： 尚未修改
* 修改人： 尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.14
'''


class MinCapitalGainAutoCorr(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.volume_adj_minute",
                   "FactorData.Basic_factor.amt_minute",
                   "FactorData.Basic_factor.free_float_shares",
                   "FactorData.Basic_factor.close"]
    lag = 1
    minute_lag = 1
    reform_window = 11

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_adj_minute"]
        amt_minute = single_database.depend_data["FactorData.Basic_factor.amt_minute"]
        free_float_shares = single_database.depend_data["FactorData.Basic_factor.free_float_shares"]
        close = single_database.depend_data["FactorData.Basic_factor.close"]

        arr = free_float_shares.values * close.values
        free_float_cap = pd.DataFrame(arr, index=close.index, columns=close.columns)

        fmt = '%Y%m%d'
        date_list = np.unique(volume_minute.index.strftime(fmt))
        pre_date = date_list[-2]
        compute_date = date_list[-1]
        i=-60
        end=-3

        volume_df = volume_minute.loc[pre_date].iloc[i:end].append(volume_minute.loc[compute_date])
        amt_df = amt_minute.loc[pre_date].iloc[i:end].append(amt_minute.loc[compute_date])

        arr = amt_df.values / free_float_cap.loc[pre_date].values
        turn = pd.DataFrame(arr, index=amt_df.index, columns=amt_df.columns)

        arr = amt_df.values / volume_df.values
        vwap_df = pd.DataFrame(arr, index=amt_df.index, columns=amt_df.columns)

        arr = turn.values * vwap_df.shift(1).values
        rel_price = pd.DataFrame(arr, index=turn.index, columns=turn.columns)

        result = - array_coef(rel_price.rank(axis=0), rel_price.shift(1).rank(axis=0))
        return result

    def reform(self, temp_result):
        arr = temp_result.values - temp_result.shift(self.reform_window - 1).values
        ans = pd.DataFrame(arr, index=temp_result.index, columns=temp_result.columns)
        return ans
