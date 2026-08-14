import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：MinAmtMidSkew
* 逻辑：该因子是一个分钟因子，主要在于衡量分钟级的成交量加权价格变化的偏度，
* 偏度数值越大意味着收益率整体右偏越严重，行情即将结束
* 因子参数：分钟数据的高开低收
* 作者：陈卓
* 日期：2019.1.15
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.9
'''


class MinAmtMidSkew(BaseFactor):
    factor_type = "DAY"
    fix_times = ["1500"]
    depend_data = ["FactorData.Basic_factor.high_adj_minute",
                   "FactorData.Basic_factor.low_adj_minute",
                   "FactorData.Basic_factor.volume_adj_minute"]
    lag = 0
    reform_window = 20

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        high_minute = single_database.depend_data["FactorData.Basic_factor.high_adj_minute"]
        low_minute = single_database.depend_data["FactorData.Basic_factor.low_adj_minute"]
        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_adj_minute"]

        arr = (high_minute.values + low_minute.values) / 2
        mid_minute = pd.DataFrame(arr, index=high_minute.index, columns=high_minute.columns)

        arr = (volume_minute.values / volume_minute.sum().values) * (mid_minute.values / mid_minute.shift(1).values - 1)
        ratio = pd.DataFrame(arr, index=volume_minute.index, columns=volume_minute.columns)
        ans = ratio.sum()
        return ans

    def reform(self, temp_result):
        ans = - temp_result.rolling(window=self.reform_window, min_periods=10).skew()
        return ans
