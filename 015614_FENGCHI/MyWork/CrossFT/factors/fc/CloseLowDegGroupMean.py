# coding: utf-8
# Author：fengchi863
# Date ：2021/11/12 11:13

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class CloseLowDegGroupMean(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 10
    author = 'fc'
    freq = 'daily'
    logic = '收盘价相对于最低价的回归系数'
    article = ''
    basic_datas = {'daily': ['low_badj', 'close_badj'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        low = self.database['daily']['low_badj']
        deg = dt_alpha2(close, low, 10)
        return deg

    def calc_groupst(self):
        indicator = self.st_factor()
        group = sameshape(indicator, self.group_factor())
        group_ret = st2groupst(indicator, group, cross_mean)
        ret = arr_match_index(group_ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = CloseLowDegGroupMean(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()