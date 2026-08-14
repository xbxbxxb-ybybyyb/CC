import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef
from xfactor.FixUtil import minute_data_transform, min_forward_adj

'''
* 因子名：MinPre30mAutoCorr
* 因子功能描述：计算昨日尾盘与当日分钟最高价与最低价价格差值与开盘价之间的秩相关性，是一个反转因子，该值越大则越容易往下跌
* 因子参数：  MinuteClose,MinuteHigh, MinuteLow
* 作者： 肖倩
* 因子创建日期： 2019.7.8
* 函数修改日期： 尚未修改
* 修改人： 尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.14
'''


class MinPre30mAutoCorr(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.open_adj_minute",
                   "FactorData.Basic_factor.high_adj_minute",
                   "FactorData.Basic_factor.low_adj_minute"]
    lag = 0
    minute_lag = 1

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        open_minute = single_database.depend_data["FactorData.Basic_factor.open_adj_minute"]
        high_minute = single_database.depend_data["FactorData.Basic_factor.high_adj_minute"]
        low_minute = single_database.depend_data["FactorData.Basic_factor.low_adj_minute"]

        fmt = '%Y%m%d'
        date_list = np.unique(open_minute.index.strftime(fmt))
        pre_date = date_list[-2]
        compute_date = date_list[-1]

        high_df = high_minute.loc[pre_date].iloc[-30:].append(high_minute.loc[compute_date])
        low_df = low_minute.loc[pre_date].iloc[-30:].append(low_minute.loc[compute_date])
        open_df = open_minute.loc[pre_date].iloc[-30:].append(open_minute.loc[compute_date])

        arr = high_df.values - low_df.values
        diff = pd.DataFrame(arr, index=high_df.index, columns=high_df.columns)
        result = - array_coef(diff, open_df)
        return result
