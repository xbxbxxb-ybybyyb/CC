import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

'''
* 因子名称：LowSharpeAmountStdRatio_13h
* 描述：收益率滚动10分钟Sharpe最低时的成交额标准差 / 当日开盘至11:30成交额标准差
* 因子逻辑：股价下跌时段的成交额标准差如果特别大，说明下跌引起的过度反应比较明显，可能存在超跌的情况
* 因子参数：分钟数据的成交额、成交量
* 作者：何丰敬
* 日期：2019.9.22
* 函数修改日期:尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.13
'''


class LowSharpeAmountStdRatio(BaseFactor):
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

        # 超额收益
        arr = r.values - r.mean(axis=1).values.reshape(r.shape[0], 1)
        r = pd.DataFrame(arr, index=r.index, columns=r.columns)

        # 滚动10分钟sharpe
        r_rolling = r.rolling(10)

        arr = r_rolling.mean().values / r_rolling.std().values
        s_rolling = pd.DataFrame(arr, index=r.index, columns=r.columns)

        s_rolling_min = s_rolling.min()
        amount_std = amt_minute.rolling(10).std()

        arr = s_rolling.values == s_rolling_min.values
        df = pd.DataFrame(arr, index=s_rolling.index, columns=s_rolling.columns)

        amount_std = amount_std[df].mean()  # 筛选出滚动10分钟sharpe最低时的成交额标准差
        arr = amount_std.values / amt_minute.std().values

        ans = pd.Series(arr, index=volume_minute.columns)
        return ans
