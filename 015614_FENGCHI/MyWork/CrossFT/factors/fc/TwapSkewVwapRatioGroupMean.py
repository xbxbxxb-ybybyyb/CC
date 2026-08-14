# coding: utf-8
# Author：fengchi863
# Date ：2021/11/8 14:12

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class TwapSkewVwapRatioGroupMean(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 0
    author = 'fc'
    freq = '1min'
    logic = 'twap偏度与vwap之比(偏度越小上涨概率越大) 组内求平均'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['amt', 'close_badj']}

    def st_factor(self):
        amt = self.database['1min']['amt']
        close = self.database['1min']['close_badj']

        vwap = ts_cumsum(close * amt) / ts_cumsum(amt)
        twap = ts_cummean(close)
        ret = ts_cumskew(twap) / vwap
        return ret

    def calc_groupst(self):
        ret = self.st_factor()
        group = sameshape(ret, self.group_factor())
        ret = st2groupst(ret, group, cross_mean)
        factor = arr_match_index(ret, self.cal_date_range, self.date_range)
        return factor

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = TwapSkewVwapRatioGroupMean()
    # print(f.result())

    cal_factor()
