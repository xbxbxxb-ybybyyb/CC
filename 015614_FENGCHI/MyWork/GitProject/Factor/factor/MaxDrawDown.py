import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：MaxDrawDown_13h
* 因子功能描述：截至13:00分钟收盘价的最大回撤-前一日最大回撤
* 当日收益具有动量效应、前一日具有反转效应，将二者结合，构建复合下跌支撑指标，该值越大，前一日回撤较大，当日回撤较小，易上涨。
* 因子参数：[MinuteClose]: 分钟收盘价
* 作者：周璇
* 因子创建日期：2019.7.23
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.14
'''


class MaxDrawDown(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.close_adj_minute"]
    lag = 0
    minute_lag = 1

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]

        fmt = '%Y%m%d'
        date_list = sorted(np.unique(close_minute.index.strftime(fmt)))
        date = date_list[-1]
        pre_date = date_list[-2]

        close = pd.concat([close_minute.loc[pre_date].iloc[-1:], close_minute.loc[date]])
        close_pre = close_minute.loc[pre_date]

        def max_drawdown_parallel(df):
            # 把整列为nan的变成0
            df.loc[:, np.isnan(df).all()] = 0
            # 获得每一列的index
            idx_array = np.ones([df.shape[0], df.shape[1]]) * np.array(range(df.shape[0])).reshape(df.shape[0], 1)
            # 计算end_index以及保留对应的值
            end_idx = np.nanargmax(np.fmax.accumulate(df).values - df.values, axis=0)
            mask1 = pd.DataFrame(idx_array == end_idx, index=df.index, columns=df.columns)
            end_values = df[mask1].mean().values
            # 求得start_value
            mask2 = pd.DataFrame(idx_array < end_idx, index=df.index, columns=df.columns)
            start_value = np.nanmax(df[mask2].values, axis=0)
            # 计算每只股票的最大回撤
            ans = pd.Series((end_values - start_value) / start_value)
            return ans

        arr = max_drawdown_parallel(close).values - max_drawdown_parallel(close_pre).values
        maxdrawdown = pd.Series(arr, index=close_minute.columns)

        return maxdrawdown
