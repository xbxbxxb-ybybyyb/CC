import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：MinCapitalGainOverhang
* 因子功能描述：计算最高价格相对于参考价格的位置。
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


class MinCapitalGainAbs(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.open_adj_minute",
                   "FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.high_adj_minute",
                   "FactorData.Basic_factor.low_adj_minute"]
    lag = 0
    reform_window = 11

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        open_minute = single_database.depend_data["FactorData.Basic_factor.open_adj_minute"]
        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        high_minute = single_database.depend_data["FactorData.Basic_factor.high_adj_minute"]
        low_minute = single_database.depend_data["FactorData.Basic_factor.low_adj_minute"]

        arr = (high_minute.values - low_minute.values) - abs(open_minute.values - close_minute.values)
        rel_price = pd.DataFrame(arr, index=close_minute.index, columns=close_minute.columns)

        result = - array_coef(rel_price.rank(axis=0), high_minute.rank(axis=0))
        return result

    def reform(self, temp_result):
        arr = temp_result.values - temp_result.shift(self.reform_window - 1).values
        ans = pd.DataFrame(arr, index=temp_result.index, columns=temp_result.columns)
        return ans
