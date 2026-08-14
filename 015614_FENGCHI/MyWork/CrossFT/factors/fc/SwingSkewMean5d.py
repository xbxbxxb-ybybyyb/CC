# coding: utf-8
# Author：fengchi863
# Date ：2021/10/14 18:09

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class SwingSkewMean5d(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 10
    author = 'fc'
    freq = 'daily'
    logic = '每分钟振幅的skew值，求5日均值'
    article = ''
    basic_datas = {'daily': [], '30min': [], '5min': [], '1min': ['high', 'low']}

    def st_factor(self):
        high = self.database['1min']['high']
        low = self.database['1min']['low']
        swing = (high - low) / low
        EX = np.nanmean(swing, axis=1, keepdims=True)
        EX2 = np.nanmean((swing - EX) ** 2, axis=1)
        EX3 = np.nanmean((swing - EX) ** 3, axis=1)
        skew = EX3 / EX2 ** 1.5
        return skew

    def cal_groupst(self):
        skew = self.st_factor()
        group = sameshape(skew, self.group_factor())
        ret = st2groupst(skew, group,  self.group_func())
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    # f = SwingKurtMean5d(start=20210401, end=20210501)
    # print(f.result())

    val = cal_factor('/data/user/015614/MyWork/CrossFT/factors/fc', 'SwingSkewMean5d.py', {'daily': 6}, notrun=False)
