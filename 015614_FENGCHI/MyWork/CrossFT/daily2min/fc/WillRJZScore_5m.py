# coding: utf-8
# Author：fengchi863
# Date ：2021/9/6 11:03

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *
import talib

'''
一种方式：ZSCORE
'''


class WillRJZScore_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 20
    author = 'fc'
    freq = '5mins'
    logic = '行业内个股的威廉指标ZScore'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': ['close_badj', 'high_badj', 'low_badj'], '1min': []}

    def st_factor(self):
        close = self.database['5mins']['close_badj'].reshape(-1, 1)
        high = self.database['5mins']['high_badj'].reshape(-1, 1)
        low = self.database['5mins']['low_badj'].reshape(-1, 1)
        willr = talib.WILLR(high[:, 0], low[:, 0], close[:, 0])
        ret = willr.reshape(len(self.cal_date_range), 48, -1)
        return ret

    def calc_groupst(self):
        ret = self.st_factor()
        self.group = sameshape(ret, self.group_factor())

        MEAN = st2groupst(ret, self.group, cross_mean)
        STD = st2groupst(ret, self.group, cross_std)
        ret = (ret - MEAN) / STD
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = WillRJZScore_5m()
    # print(f.result())
    cal_factor()
