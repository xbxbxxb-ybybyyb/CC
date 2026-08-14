# coding: utf-8
# Author：fengchi863
# Date ：2021/11/11 14:24

'''
动量型因子
'''

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class VolRatioGroupInc_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 2
    author = 'fc'
    freq = '5mins'
    logic = '该五分钟成交量占上一个五分钟成交量之比，板块增长加速度'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': ['volume'], '1min': []}

    def st_factor(self):
        vol = self.database['5mins']['volume']

        ret = vol / dt_delay(vol, 1)
        return ret

    def calc_groupst(self):
        indicator = self.st_factor()
        group = sameshape(indicator, self.group_factor())
        group_mean = st2groupst(indicator, group, cross_mean)
        ret = group_mean / dt_delay(group_mean, 1)
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = VolRatioGroupInc_5m(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
