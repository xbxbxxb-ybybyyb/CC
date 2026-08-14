import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

'''
* 因子功能描述 : 股票5日内成交额波动率与当日尾盘振幅共同作用
* 因子参数 : Minute_Status, MinuteClose, adjfactor, is_valid_raw
* 作者 : 肖倩
* 因子创建日期 : 2018.01.02
* 函数修改日期 : 尚未修改
* 修改人 ：尚未修改
* 修改原因 :  尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.10
'''


class MinuteAmtStdSwing(BaseFactor):
    factor_type = "DAY"
    fix_times = ["1500"]
    depend_data = ["FactorData.Basic_factor.high_adj_minute",
                   "FactorData.Basic_factor.low_adj_minute",
                   "FactorData.Basic_factor.is_valid",
                   "FactorData.Basic_factor.amt"]
    lag = 4

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        # 分钟频
        high_minute = single_database.depend_data["FactorData.Basic_factor.high_adj_minute"]
        low_minute = single_database.depend_data["FactorData.Basic_factor.low_adj_minute"]
        # 日频
        is_valid = single_database.depend_data["FactorData.Basic_factor.is_valid"]
        amt = single_database.depend_data["FactorData.Basic_factor.amt"]

        def minute(MinuteHigh, MinuteLow):
            fmt = '%Y%m%d'
            date_list = np.unique(MinuteHigh.index.strftime(fmt))
            df_ratio = pd.DataFrame(index=date_list, columns=MinuteHigh.columns)
            for date in date_list:
                high = MinuteHigh.loc[date]
                low = MinuteLow.loc[date]
                wave30 = high.iloc[-30:].max().values - low.iloc[-30:].min().values
                wave = high.max().values - low.min().values
                df_ratio.loc[date] = wave30 / wave
            return df_ratio

        high_minute_day_df = minute(high_minute, low_minute)

        # 过滤
        alpha_day = amt.rolling(window=5).std()
        alpha_day[~np.isfinite(alpha_day)] = np.nan
        alpha_day[pd.DataFrame(is_valid.values == 0, index=alpha_day.index, columns=alpha_day.columns)] = np.nan

        a = alpha_day.rank(axis=1).iloc[-1, :]
        b = high_minute_day_df.rank(axis=1).iloc[-1, :]

        # 合并分钟级和日频
        alpha = - (a + b)

        return alpha