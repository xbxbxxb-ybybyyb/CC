# coding: utf-8
# Author：fengchi863
# Date ：2021/9/1 10:15

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class InterLowHighMaxPct(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 3
    author = 'fc'
    freq = 'daily'
    logic = '前后两日最低价与最高价的最高变化率'
    article = ''
    basic_datas = {'daily': ['high_badj', 'low_badj'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        high_badj = self.database['daily']['high_badj']
        low_badj = self.database['daily']['low_badj']
        pct = (high_badj - low_badj) / low_badj
        return pct

    def calc_groupst(self):
        pct = self.st_factor()
        self.group = sameshape(pct, self.group_factor())
        cum_corr = dt_max(pct, 2)
        ret = st2groupst(cum_corr, self.group, cross_mean)
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    f = InterLowHighMaxPct()
    print(f.result())
    f.save_result()
