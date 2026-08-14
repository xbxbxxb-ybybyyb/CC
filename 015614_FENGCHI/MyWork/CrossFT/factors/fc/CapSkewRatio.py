# coding: utf-8
# Author：fengchi863
# Date ：2021/8/30 13:23

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class CapSkewRatio(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 0
    start = 20140701
    # start = 20210401
    end = 20210531
    author = 'fc'
    freq = '1min'
    logic = '主买主卖时段容量的偏度对比'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['activebuyorderamt', 'activesellorderamt']}

    def st_factor(self):
        activebuyorderamt = self.database['1min']['activebuyorderamt']
        activesellorderamt = self.database['1min']['activesellorderamt']
        return activebuyorderamt, activesellorderamt

    def calc_groupst(self):
        activebuyorderamt, activesellorderamt = self.st_factor()
        self.group = sameshape(activebuyorderamt, self.group_factor())
        group_activebuyorderamt = st2groupst(activebuyorderamt, self.group, cross_sum)
        group_activesellorderamt = st2groupst(activesellorderamt, self.group, cross_sum)
        group_buy_skew = ts_cumskew(group_activebuyorderamt)
        group_sell_skew = ts_cumskew(group_activesellorderamt)
        ret = group_buy_skew / group_sell_skew
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    f = CapSkewRatio()
    print(f.result())
    f.save_result()
