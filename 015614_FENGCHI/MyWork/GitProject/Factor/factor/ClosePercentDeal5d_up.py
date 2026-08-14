import numpy as np
import pandas as pd
from collections import Counter
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：ClosePercentDeal5d_up
* 因子功能描述：每笔成交额较大的市场下收盘价百分比的5日均值
* 因子参数：[MinuteClose]: 分钟收盘价
           [amt]: 成交额
           [dealnum]: 交易笔数
           [n]: 回看天数

* 作者：周璇
* 因子创建日期：2019.4.18
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.10
'''


class ClosePercentDeal5d_up(BaseFactor):
    factor_type = "DAY"
    fix_times = ["1500"]
    depend_data = ["FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.amt",
                   "FactorData.Basic_factor.dealnum"]
    lag = 4

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        amt = single_database.depend_data["FactorData.Basic_factor.amt"]
        dealnum = single_database.depend_data["FactorData.Basic_factor.dealnum"]

        def minute(MinuteClose):
            fmt = '%Y%m%d'
            datelist = np.unique(MinuteClose.index.strftime(fmt))
            ClosePercent = pd.DataFrame(index=datelist, columns=MinuteClose.columns)

            for date in datelist:
                close = MinuteClose.loc[date]  # pd.DataFrame
                close_arr = close.values       # np.array()
                result = np.array([np.nan] * close.shape[1])
                for j in range(close.shape[1]):
                    mylist = close_arr[:, j]
                    if ~np.isnan(close_arr[-1, j]) and Counter(np.isnan(mylist))[0] >= 200:
                        ind = np.where(~np.isnan(mylist))[0]
                        sort = np.sort((mylist)[ind])
                        if close_arr[-1, j] < sort[0]:
                            result[j] = (close_arr[-1, j] - sort[0]) / abs(sort[0])
                        elif close_arr[-1, j] >= sort[-1]:
                            result[j] = 1 + (close_arr[-1, j] - sort[-1]) / abs(sort[-1])
                        else:
                            bigger_this_data = np.where(sort >= close_arr[-1, j])[0]
                            result[j] = bigger_this_data[0] / (len(sort) + 1)
                ClosePercent.loc[date] = result

            ClosePercent = ClosePercent.convert_objects(convert_numeric=True)
            return ClosePercent

        n = 5

        ClosePercent = minute(close_minute)  # 拿到前5天的所有（计算好的）分钟日频数据

        D = pd.DataFrame(amt.values / dealnum.values, index=amt.index, columns=amt.columns)
        D[np.isinf(D)] = np.nan
        D_median = D.rolling(window=n, min_periods=int(n*0.8)).median()

        ClosePercentDeal5d_up = pd.DataFrame(index=ClosePercent.index[n-1:], columns=ClosePercent.columns)
        for date in ClosePercentDeal5d_up.index[-1:].to_list():
            D_temp = D.loc[:date].iloc[-n:]  # DataFrame
            D_med = pd.DataFrame([D_median.loc[date].values.tolist()]*n, index=D_temp.index, columns=D_temp.columns)
            higher = pd.DataFrame(D_temp.values >= D_med.values, index=D_med.index, columns=D_med.columns)  # 选出哪些天，哪些股票符合条件
            ClosePercentDeal5d_up.loc[date] = (ClosePercent.loc[D_temp.index])[higher].mean(axis=0).values

        return -ClosePercentDeal5d_up.iloc[-1, :]

