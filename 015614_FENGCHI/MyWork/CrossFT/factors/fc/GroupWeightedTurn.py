# coding: utf-8
# Author：fengchi863
# Date ：2021/9/8 15:55

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class GroupWeightedTurn(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 10
    author = 'fc'
    freq = 'daily'
    logic = '当天个股换手率 * 当天组内成交额/组内自由流通市值'
    article = ''
    basic_datas = {'daily': ['turn', 'amt', 'free_float_shares'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        turn = self.database['daily']['turn']
        amt = self.database['daily']['amt']
        free_float_shares = self.database['daily']['free_float_shares']
        return turn, amt, free_float_shares

    def calc_groupst(self):
        turn, amt, free_float_shares = self.st_factor()
        self.group = sameshape(turn, self.group_factor())
        group_turn = st2groupst(amt, self.group,  self.group_func()) / st2groupst(free_float_shares, self.group, self.group_func())
        ret = turn * group_turn
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    f = GroupWeightedTurn()
    f.save_result()
