# coding: utf-8
# Author：fengchi863
# Date ：2021/11/10 15:17

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class HighCloseDistanceGroupMean(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 2
    author = 'fc'
    freq = '1min'
    logic = '分钟最高价到当前价格的变化率，分组求平均'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['close_badj']}

    def st_factor(self):
        close = self.database['1min']['close_badj']
        max_close = ts_cummax(close)
        pct = close / max_close - 1
        return pct

    def calc_groupst(self):
        indicator = self.st_factor()
        group = sameshape(indicator, self.group_factor())
        group_ret = st2groupst(indicator, group,  self.group_func())
        ret = arr_match_index(group_ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = HighCloseDistanceGroupMean(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
