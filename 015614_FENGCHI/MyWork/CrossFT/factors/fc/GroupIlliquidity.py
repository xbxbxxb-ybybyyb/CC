# coding: utf-8
# Author：fengchi863
# Date ：2021/9/6 13:27

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *
import talib

'''
个股*组值均值
'''


class GroupIlliquidity(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 20
    author = 'fc'
    freq = 'daily'
    logic = '行业内个股的非流动性 abs(turn)/ret 个股*组值'
    article = ''
    basic_datas = {'daily': ['turn', 'pct_chg'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        return self.database['daily']['turn'], self.database['daily']['pct_chg']

    def calc_groupst(self):
        turnover, pctchg = self.st_factor()
        self.group = sameshape(turnover, self.group_factor())
        illiquidity = abs(pctchg) / turnover
        group_illiquidity = st2groupst(illiquidity, self.group, cross_mean)
        ret = illiquidity * group_illiquidity
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    f = GroupIlliquidity()
    print(f.result())
    f.save_result()
