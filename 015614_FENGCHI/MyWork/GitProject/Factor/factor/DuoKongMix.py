import time
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 因子名 : DuoKongMix
* 因子功能描述 : 计算分钟级高频数据因子，利用价格与多均线之间的面积，并辅助成交量占比加权，并结合日线多空博弈指标和近期换手率指标
* 因子参数 : MinuteTurnover-成交额 MinuteVolume-成交量 MinuteOpen-开盘价
* 函数返回值 : 多空博弈因子
* 作者 : 孙海平
* 因子创建日期 : 2018.12.26
* 函数修改日期 : 尚未修改
* 修改人 ：尚未修改
* 修改原因 :  尚未修改
* 版本 : 1.0
* 历史版本 : 无
* 迁移作者：015625
* 迁移日期：2020.1.22
'''


class DuoKongMix(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.volume_minute",
                   "FactorData.Basic_factor.amt_minute",
                   "FactorData.Basic_factor.open_minute",
                   "FactorData.Basic_factor.open_badj",
                   "FactorData.Basic_factor.high_badj",
                   "FactorData.Basic_factor.low_badj",
                   "FactorData.Basic_factor.close_badj",
                   "FactorData.Basic_factor.amt",
                   "FactorData.Basic_factor.free_float_shares"]
    lag = 5

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_minute"]
        amt_minute = single_database.depend_data["FactorData.Basic_factor.amt_minute"]
        open_minute = single_database.depend_data["FactorData.Basic_factor.open_minute"]

        open_badj = single_database.depend_data["FactorData.Basic_factor.open_badj"]
        high_badj = single_database.depend_data["FactorData.Basic_factor.high_badj"]
        low_badj = single_database.depend_data["FactorData.Basic_factor.low_badj"]
        close_badj = single_database.depend_data["FactorData.Basic_factor.close_badj"]

        amt = single_database.depend_data["FactorData.Basic_factor.amt"]
        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_minute"]
        free_float_shares = single_database.depend_data["FactorData.Basic_factor.free_float_shares"]
        free_float_cap = pd.DataFrame(free_float_shares.values * close_badj.values,
                                      index=close_badj.index,
                                      columns=close_badj.columns)

        arr = abs(high_badj.values - low_badj.values) / abs(open_badj.values - close_badj.values)
        duokong_daily = pd.DataFrame(arr, index=close_badj.index, columns=close_badj.columns)

        arr = amt.values / free_float_cap.values
        turn_rate = pd.DataFrame(arr, index=amt.index, columns=amt.columns)

        turn_rate_rank = turn_rate.rank(pct=True, axis=1)

        up_var = self.minute(amt_minute, volume_minute, open_minute)

        arr = up_var.values * (1 + turn_rate_rank.values) * (1 + duokong_daily.values)
        up_var = pd.DataFrame(arr, index=up_var.index, columns=up_var.columns)

        arr = up_var.rolling(window=5, min_periods=1).mean() / \
                      up_var.rolling(window=5, min_periods=1).std()
        up_var_stat = pd.DataFrame(-arr, index=up_var.index, columns=up_var.columns)
        up_var_stat[np.isinf(up_var_stat)] = np.nan
        return up_var_stat.iloc[-1, :]

    def minute(self, MinuteTurnover, MinuteVolume, MinuteOpen):
        """

        *因子名 : DuoKongMix
        *因子功能描述 : 计算分钟级高频数据因子，利用价格与多均线之间的面积，并辅助成交量占比加权，并结合日线多空博弈指标和近期换手率指标
        *因子参数 : MinuteTurnover-成交额 MinuteVolume-成交量 MinuteOpen-开盘价
        *函数返回值 : 多空博弈因子
        *作者 : 孙海平
        *因子创建日期 : 2018.12.26
        *函数修改日期 : 尚未修改
        *修改人 ：尚未修改
        *修改原因 :  尚未修改
        *版本 : 1.0
        *历史版本 : 无

        """
        fmt = '%Y%m%d'
        date_list = np.unique(MinuteTurnover.index.strftime(fmt))
        df_skew = pd.DataFrame(index=date_list, columns=MinuteTurnover.columns)
        weight = np.array([1 + i / 480 for i in range(0, 240)])
        weight = weight.reshape(240, 1)

        for date in date_list:
            turnover = MinuteTurnover.loc[date]
            volume = MinuteVolume.loc[date]
            Open = MinuteOpen.loc[date]

            arr = turnover.values / volume.values
            vwap = pd.DataFrame(arr, index=volume.index, columns=volume.columns)

            price_open = Open.iloc[0]
            vwap[vwap.gt(price_open * 1.2, axis=1) & ~vwap.gt(price_open * 0.8, axis=1)] = np.nan
            vwap.fillna(method='ffill', inplace=True)

            arr = volume.values / volume.sum(axis=0).values
            turn_ratio = pd.DataFrame(arr, index=volume.index, columns=volume.columns)

            vwapRolling5 = vwap.rolling(window=2, min_periods=1).mean()
            vwapRolling10 = vwap.rolling(window=5, min_periods=1).mean()
            vwapRolling20 = vwap.rolling(window=10, min_periods=1).mean()

            arr = vwap.values - (vwapRolling5.values + vwapRolling10.values + vwapRolling20.values) / 3
            DuoKong = pd.DataFrame(arr, index=vwap.index, columns=vwap.columns)

            arr = abs(DuoKong.values) < (np.max(abs(DuoKong.values), axis=0) * 0.1)
            mask = pd.DataFrame(arr, index=DuoKong.index, columns=DuoKong.columns)
            DuoKong[mask] = np.nan

            DuoKong_weight = pd.DataFrame(data=DuoKong.values * weight, index=DuoKong.index, columns=DuoKong.columns)

            arr = DuoKong_weight.values * turn_ratio.values
            DuoKong_weight2 = pd.DataFrame(arr, index=DuoKong_weight.index,
                                           columns=DuoKong_weight.columns)

            DuoKong_weight_sums = DuoKong_weight2.sum(axis=0)
            df_skew.loc[date] = DuoKong_weight_sums
        return df_skew

