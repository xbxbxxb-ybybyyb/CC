import time
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：RetStdTurnCorr
* 因子功能描述：
 - 计算公式
    a = TSRank(std(close / Delay(close, 1) - 1, 5), 20)
    b = TSRank(turn, 20)
    ans = - Corr(a, b, 20)
 - 编写逻辑
    收益率的5日波动率的近20日时序排名，与换手率的近20日时序排名，之间相关性的相反数
* 因子参数： pct_chg, turn
* 作者：王海洋
* 因子创建时间： 2019.02.24
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改 
'''


class RetStdTurnCorr(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.pct_chg",
                   "FactorData.Basic_factor.turn"]
    lag = 30

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        pct_chg = single_database.depend_data["FactorData.Basic_factor.pct_chg"]
        turn = single_database.depend_data["FactorData.Basic_factor.turn"]

        std = pct_chg.rolling(5).std()

        a = std.tail(20).rank(axis=1)
        b = turn.tail(20).rank(axis=1)

        ans = - array_coef(a, b)

        return ans

