# coding: utf-8
# Author：fengchi863
# Date ：2021/12/17 15:11

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class PSCorrMean(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 60
    author = 'fc'
    freq = 'daily'
    logic = '均价与均价标准差相关性的5日平均，组内求均值'
    article = ''
    basic_datas = {'daily': ['twap'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        twap = self.database['daily']['twap']
        ret = dt_mean(dt_corr2(twap, dt_std(twap, 20), 30), 5)
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
    # f = PSCorrMean(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()