# coding: utf-8
# Author：fengchi863
# Date ：2021/9/9 9:56

import bottleneck
import numpy as np

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class MktDragonStkRetWithOthers(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 20
    author = 'fc'
    # logic = '个股收益率 - 组内龙头个股（按市值）的平均收益率'
    logic = '组内龙头个股（按市值）的平均收益率'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['pct_chg', 'a_mkt_cap']}

    def st_factor(self):
        pctchg = self.database['daily']['pct_chg']
        return pctchg

    def cal_groupst(self):
        pctchg = self.st_factor()
        a_mkt_cap = self.database['daily']['a_mkt_cap']
        stgroup = sameshape(a_mkt_cap, self.group_factor())
        groups = np.unique(stgroup[np.isfinite(stgroup)])
        shape = a_mkt_cap.shape
        rank = np.full(a_mkt_cap.shape, np.nan)
        for g in groups:
            val = stgroup == g
            rank = np.where(val, bottleneck.nanrankdata(np.where(val, -a_mkt_cap, np.nan), axis=len(shape) - 1), rank)
        pctchg[rank > 5] = np.nan
        res = st2groupst(pctchg, stgroup, cross_mean)
        return res

    def cal_customst(self):
        # factor = self.st_factor() - self.cal_groupst()
        factor = self.cal_groupst()
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_customst()


if __name__ == '__main__':
    f = MktDragonStkRetWithOthers()
    f.result()
    f.save_result()
