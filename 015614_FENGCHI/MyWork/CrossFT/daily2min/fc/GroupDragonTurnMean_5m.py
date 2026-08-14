# coding: utf-8
# Author：fengchi863
# Date ：2021/9/9 9:56

import bottleneck
import numpy as np

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class GroupDragonTurnMean_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 5
    author = 'fc'
    logic = '组内龙头个股（按市值）日内换手率'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['a_mkt_cap'], '5mins': ['amt']}

    def st_factor(self):
        amt = self.database['5mins']['amt']
        a_mkt_cap = self.database['daily']['a_mkt_cap']
        amt_sum = ts_cumsum(amt) / a_mkt_cap
        return amt_sum

    def cal_groupst(self):
        amt_sum = self.st_factor()
        a_mkt_cap = self.database['daily']['a_mkt_cap']
        stgroup = sameshape(a_mkt_cap, self.group_factor())
        groups = np.unique(stgroup[np.isfinite(stgroup)])
        shape = a_mkt_cap.shape
        rank = np.full(amt_sum.shape, np.nan)
        for g in groups:
            val = stgroup == g
            rank = np.where(val, bottleneck.nanrankdata(np.where(val, -a_mkt_cap, np.nan), axis=len(shape) - 1), rank)
        amt_sum[rank > 5] = np.nan
        res = st2groupst(amt_sum, stgroup, cross_mean)
        return res

    def cal_customst(self):
        # factor = self.st_factor() - self.cal_groupst()
        factor = self.cal_groupst()
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_customst()


if __name__ == '__main__':
    f = GroupDragonTurnMean_5m(start=20210401, end=20210501)
    f.result()

    cal_factor()

