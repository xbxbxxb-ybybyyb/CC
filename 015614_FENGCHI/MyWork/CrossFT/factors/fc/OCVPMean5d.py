# coding: utf-8
# Author：fengchi863
# Date ：2021/9/14 14:57

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class OCVPMean5d(crossFactor):
    cross_group = 'sw2'
    cross_func = 'cross_mean'
    extend_days = 10
    author = 'fc'
    freq = 'daily'
    logic = '个股开盘集合竞价阶段成交量占比5日均值 - 组内集合竞价阶段成交量占比5日均值'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['amt']}

    def st_factor(self):
        amt = self.database['1min']['amt']
        return amt

    def calc_groupst(self):
        amt = self.st_factor()
        amt1 = amt[:, [0], :]
        amt2 = np.nansum(amt, axis=1, keepdims=True)
        call_auction_amt_pct = amt1 / amt2
        stk_mean = dt_mean(call_auction_amt_pct, 5)
        self.group = sameshape(amt1, self.group_factor())
        group_call_auction_amt_pct = st2groupst(amt1, self.group, cross_sum) / st2groupst(amt2, self.group, cross_sum)
        group_mean = dt_mean(group_call_auction_amt_pct, 5)
        ret = stk_mean - group_mean
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily':20})
    gap = abs(val1 - val2)/abs(val1)
    print(np.sum(np.where(np.isfinite(gap), gap, 0)))
