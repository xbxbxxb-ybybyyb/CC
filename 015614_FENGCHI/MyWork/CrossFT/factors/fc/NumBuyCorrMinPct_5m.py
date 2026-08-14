# coding: utf-8
# Author：fengchi863
# Date ：2021/12/30 16:34

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class NumBuyCorrMinPct_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 2
    author = 'fc'
    freq = '5mins'
    logic = '总成交笔数与分钟涨跌幅的相关性，分组求平均'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': ['num_total', 'close_badj'], '1min': []}

    def st_factor(self):
        close = self.database['5mins']['close_badj']
        num_total = self.database['5mins']['num_total']
        pct_chg = dt_pct(close, 1)
        ret = dt_corr2(pct_chg, num_total, 48)
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
    # f = NumBuyCorrMinPct_5m(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
