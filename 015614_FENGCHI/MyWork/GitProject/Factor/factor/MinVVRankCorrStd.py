import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import xfactor.Util as Util

"""
* 因子名 : MinVVRankCorrStd
* 因子功能描述 : （尾盘半小时量价相关性）*（vwap与vol的相关性值的rank）的5日波动率
* 因子参数 : MinuteVolume-成交量 MinuteClose-分钟收盘价
* 作者 : 薛晓伟
* 因子创建日期 : 2019.02.18
* 函数修改日期 : 尚未修改
* 修改人 ：尚未修改
* 修改原因 :  尚未修改
* 版本 : 1.0
* 历史版本 : 无
* 迁移作者：015625
* 迁移日期：2020.1.10
"""


class MinVVRankCorrStd(BaseFactor):
    factor_type = "DAY"
    fix_times = ["1500"]
    depend_data = ["FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.volume_adj_minute",
                   "FactorData.Basic_factor.volume",
                   "FactorData.Basic_factor.vwap",
                   "FactorData.Basic_factor.adjfactor"]
    lag = 5
    reform_window = 5

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_adj_minute"]
        volume = single_database.depend_data["FactorData.Basic_factor.volume"]
        vwap = single_database.depend_data["FactorData.Basic_factor.vwap"]
        adjfactor = single_database.depend_data["FactorData.Basic_factor.adjfactor"]

        vwap_adj = pd.DataFrame(vwap.values * adjfactor.values, index=vwap.index, columns=vwap.columns)

        fmt = '%Y%m%d'
        date_list = np.unique(volume_minute.index.strftime(fmt))
        df = pd.DataFrame(index=date_list, columns=volume_minute.columns)

        for date in date_list:
            c = close_minute.loc[date]
            v = volume_minute.loc[date]
            vol_close_corr = Util.array_coef(c[-30:], v[-30:])
            df.loc[date] = vol_close_corr

        vwap_vol_corr = Util.rolling_corr(vwap_adj, volume, self.reform_window)
        vwap_vol_corr_rank = vwap_vol_corr.rank(pct=True,axis=1)

        arr = vwap_vol_corr_rank.values * df.values
        result = pd.DataFrame(arr, index=vwap_vol_corr_rank.index, columns=vwap_vol_corr_rank.columns)
        return result.iloc[-1, :]

    def reform(self, temp_result):
        result = - temp_result.rolling(window=self.reform_window, min_periods=1).std()
        return result

