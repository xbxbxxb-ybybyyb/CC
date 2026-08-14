import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

'''
* 因子名称：LowStdAmountRatio_13h
* 描述：开盘至13:00波动率最低时的成交额占比
* 因子逻辑：低波动时段的成交额占比越大，则高波动时间段成交额占比越少，说明噪音交易者越少
* 因子参数：分钟数据的成交额、成交量
* 作者：何丰敬
* 日期：2019.9.11
* 函数修改日期:尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.14
'''


class LowStdAmountRatio(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.volume_adj_minute",
                   "FactorData.Basic_factor.amt_minute"]
    lag = 0

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_adj_minute"]
        amt_minute = single_database.depend_data["FactorData.Basic_factor.amt_minute"]

        arr = amt_minute.cumsum().values / volume_minute.cumsum().values
        df = pd.DataFrame(arr, index=volume_minute.index, columns=volume_minute.columns)

        arr = df.values / df.shift(1).values - 1
        r = pd.DataFrame(arr, index=df.index, columns=df.columns)

        std = r.rolling(20).std()  # 计算滚动20分钟波动率
        std_min = std.min()  # pd.Series

        # 滚动20分钟平均成交额 / 上午平均成交额
        arr = amt_minute.rolling(20).mean().values / amt_minute.mean().values
        amount = pd.DataFrame(arr, index=volume_minute.index, columns=volume_minute.columns)

        # 筛选出波动率最低时刻的成交额之比
        arr = std_min.values == std.values
        df = pd.DataFrame(arr, index=std.index, columns=std.columns)

        ans = amount[df].mean()
        return ans