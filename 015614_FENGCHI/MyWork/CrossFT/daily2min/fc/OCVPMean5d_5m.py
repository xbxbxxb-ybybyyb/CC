# coding: utf-8
# Author：fengchi863
# Date ：2021/9/14 14:57

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class OCVPMean5d_5m(crossFactor):
    cross_group = 'sw2'
    cross_func = 'cross_mean'
    extend_days = 10
    author = 'fc'
    freq = '5mins'
    logic = '个股开盘集合竞价阶段成交量占昨天比例5日均值'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': ['amt']}

    def st_factor(self):
        amt = self.database['5mins']['amt']
        yes_amt = ds_delay(amt, 1)
        return amt, yes_amt

    def calc_groupst(self):
        amt, yes_amt = self.st_factor()
        amt1 = amt[:, [0], :]
        amt2 = yes_amt[:, [0], :]
        # amt2 = np.nansum(amt, axis=1, keepdims=True)
        self.group = sameshape(amt1, self.group_factor())
        group_call_auction_amt_pct = st2groupst(amt1, self.group, cross_sum) / st2groupst(amt2, self.group, cross_sum)
        group_mean = dt_mean(group_call_auction_amt_pct, 5)
        ret = group_mean
        ret = np.repeat(ret, 48, axis=1)
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    cal_factor()
