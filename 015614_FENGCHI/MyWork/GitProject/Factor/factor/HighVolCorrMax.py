import time
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：HighVolCorrMax
* 因子功能描述：
- 计算公式
x = ROLLING_CORR(RANK(HIGH), RANK(VOLUME), 5)
ans = MAX(x, 3)
- 编写逻辑
    刻画最高价与成交量的背离程度。
    最高价与成交量在横截面的排序的5日滚动相关性，在近3日的最大值的相反数。
* 因子参数： high_badj, volume
* 作者：王海洋
* 因子创建时间： 2019.02.20
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改 
'''


class HighVolCorrMax(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.high_badj",
                   "FactorData.Basic_factor.volume"]

    lag = 20
    minute_lag = 0

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        high = single_database.depend_data["FactorData.Basic_factor.high_badj"]
        volume = single_database.depend_data["FactorData.Basic_factor.volume"]

        high_rank = high.rank(axis=1)
        volume_rank = volume.rank(axis=1)

        rank_corr = rolling_corr(high_rank, volume_rank, 5).tail(3)

        ans = - rank_corr.max(axis=0)

        return ans

