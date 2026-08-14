import time
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 因子名 : MinuteRelativeUpVar
* 因子功能描述 : 计算分钟级高频数据因子，价格上行波动率占比
* 因子参数 : path-分钟级数据路径  adjfactor-价格复权因子
* 函数返回值 : 价格上行波动率占比因子
* 作者 : 孙海平
* 因子创建日期 : 2018.12.3
* 函数修改日期 : 尚未修改
* 修改人 ：尚未修改
* 修改原因 :  尚未修改
* 版本 : 1.0
* 历史版本 : 无
* 迁移作者：015625
* 迁移日期：2020.1.22
'''


class MinuteRelativeUpVar(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.open_adj_minute",
                   "FactorData.Basic_factor.volume_minute",
                   "FactorData.Basic_factor.amt_minute"]
    lag = 5
    reform_window = 5

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        open_minute = single_database.depend_data["FactorData.Basic_factor.open_adj_minute"]
        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_minute"]
        amt_minute = single_database.depend_data["FactorData.Basic_factor.amt_minute"]

        up_var = self.minute(amt_minute, volume_minute, open_minute)
        ans = - up_var.iloc[-1]
        return ans

    def minute(self, MinuteTurnover, MinuteVolume, MinuteOpen):
        fmt = '%Y%m%d'
        date_list = np.unique(MinuteTurnover.index.strftime(fmt))
        df_skew = pd.DataFrame(index=date_list, columns=MinuteTurnover.columns)

        for date in date_list:
            turnover = MinuteTurnover.loc[date]
            volume = MinuteVolume.loc[date]
            Open = MinuteOpen.loc[date]

            arr = turnover.values / volume.values
            vwap = pd.DataFrame(arr, index=volume.index, columns=volume.columns)
            price_open = Open.iloc[0]

            mask1 = pd.DataFrame(vwap.values > price_open.values * 1.2, index=vwap.index, columns=vwap.columns)
            mask2 = pd.DataFrame(vwap.values > price_open.values * 0.8, index=vwap.index, columns=vwap.columns)

            vwap[mask1 & ~mask2] = np.nan
            vwap.fillna(method='ffill', inplace=True)

            vwap_mean = vwap.rolling(window=5).mean()
            arr = vwap.values / vwap_mean.values - 1
            chg_rate = pd.DataFrame(arr, index=vwap.index, columns=vwap.columns)

            # 计算price_up_rate
            mask = pd.DataFrame(chg_rate.values > 0, index=chg_rate.index, columns=chg_rate.columns)
            arr = chg_rate[mask].var().values / chg_rate.var().values
            up_rate = pd.Series(arr, index=chg_rate.columns)

            df_skew.loc[date] = up_rate
        return df_skew

    def reform(self, temp_result):
        temp_result = temp_result.rolling(window=self.lag, min_periods=1).mean()
        return temp_result
