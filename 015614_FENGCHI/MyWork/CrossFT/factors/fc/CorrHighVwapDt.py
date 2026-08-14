# coding: utf-8
# Author：fengchi863
# Date ：2021/9/1 14:10

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class CorrHighVwapDt(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 20
    start = 20140701
    # start = 20210401
    end = 20210531
    author = 'fc'
    freq = 'daily'
    logic = 'corr((vwap - high)/open, vwap)'
    article = ''
    basic_datas = {'daily': ['vwap', 'high', 'open'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        vwap = self.database['daily']['vwap']
        high = self.database['daily']['high']
        open = self.database['daily']['open']
        tmp1 = (vwap - high) / open
        ret = ds_corr2(tmp1, vwap, 10)
        return ret

    def calc_groupst(self):
        ret = self.st_factor()
        self.group = sameshape(ret, self.group_factor())
        ret = st2groupst(ret, self.group, cross_mean)
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily': 10})
    gap = abs(val1 - val2)
    print(np.nansum(gap))
