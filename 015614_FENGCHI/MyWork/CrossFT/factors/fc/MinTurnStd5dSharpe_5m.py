# coding: utf-8
# Author：fengchi863
# Date ：2021/12/24 15:49

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class MinTurnStd5dSharpe_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 6
    author = 'fc'
    freq = '5mins'
    logic = '分钟换手率的标准差，取5日夏普，分组求平均'
    article = ''
    basic_datas = {'daily': ['a_mkt_cap'], '30mins': [], '5mins': ['amt'], '1min': []}

    def st_factor(self):
        amt = self.database['5mins']['amt']
        cap = self.database['daily']['a_mkt_cap']
        turn = amt / cap
        ret = dt_std(turn, 12)
        ret = dt_sharpe(ret, 48 * 5)
        return ret

    def calc_groupst(self):
        indicator = self.st_factor()
        group = sameshape(indicator, self.group_factor())
        group_ret = st2groupst(indicator, group, cross_mean)
        ret = arr_match_index(group_ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = MinTurnStd5dSharpe_5m(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
