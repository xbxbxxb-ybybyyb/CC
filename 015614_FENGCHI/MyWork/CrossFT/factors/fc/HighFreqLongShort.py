# coding: utf-8
# Author：fengchi863
# Date ：2021/12/14 17:29

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class HighFreqLongShort(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 2
    author = 'fc'
    freq = '5mins'
    logic = '5分钟近似多空力量，分组求平均'
    article = ''
    basic_datas = {'daily': ['a_mkt_cap'], '30mins': [], '5mins': ['high', 'low', 'close', 'volume'], '1min': ['close_badj']}

    def st_factor(self):
        high = self.database['5mins']['high']
        low = self.database['5mins']['low']
        close = self.database['5mins']['close']
        volume = self.database['5mins']['volume']
        a_mkt_cap = self.database['daily']['a_mkt_cap']
        turnover = volume / a_mkt_cap
        ret = ((close / (high + low) * 2) - 1) * turnover
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
    # f = HighFreqLongShort(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()