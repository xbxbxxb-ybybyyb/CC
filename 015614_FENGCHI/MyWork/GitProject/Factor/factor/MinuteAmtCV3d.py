import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

"""
* 因子名 : MinuteAmtCV3d
* 因子功能描述 : 3日Amt的CV，5分钟级别
* 因子参数 : MinuteTurnover, is_valid_raw 
* 作者 : 刘正
* 因子创建日期 : 2018.01.02
* 函数修改日期 : 尚未修改
* 修改人 ：尚未修改
* 修改原因 :  尚未修改
* 迁移作者 : 015625
* 迁移日期 : 2020.1.10
"""


class MinuteAmtCV3d(BaseFactor):
    factor_type = "DAY"
    fix_times = ["1500"]
    depend_data = ["FactorData.Basic_factor.amt_minute",
                   "FactorData.Basic_factor.is_valid_raw"]
    lag = 3

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        amt_minute = single_database.depend_data["FactorData.Basic_factor.amt_minute"]
        is_valid_raw_minute = single_database.depend_data["FactorData.Basic_factor.is_valid_raw"]

        status_minute = pd.DataFrame(is_valid_raw_minute.values == 0, index=is_valid_raw_minute.index,
                                     columns=is_valid_raw_minute.columns)

        def minute(MinuteTurnover, status):
            date_list = np.unique(MinuteTurnover.index.strftime('%Y%m%d'))
            date = date_list[-1]
            AmtCV3d = []
            MinuteTurnover5min = MinuteTurnover.groupby(pd.Grouper(freq='5min')).sum().dropna(how='all')

            invalid_stock = status.columns[status.sum().values > 0]
            f = pd.Series(MinuteTurnover5min.std().values / MinuteTurnover5min.mean().values,
                          index=MinuteTurnover5min.columns)
            f.name = date
            f[invalid_stock] = np.nan
            AmtCV3d.append(f)

            MinuteAmtCV3d = pd.DataFrame(AmtCV3d)
            return MinuteAmtCV3d

        factor = minute(amt_minute, status_minute)

        factor[(is_valid_raw_minute == 0)] = np.nan
        factor = -factor
        return factor.iloc[-1, :]
