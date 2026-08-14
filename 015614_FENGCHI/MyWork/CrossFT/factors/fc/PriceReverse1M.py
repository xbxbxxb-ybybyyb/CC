# coding: utf-8
# Author：fengchi863
# Date ：2021/8/23 10:23
'''
反转类因子
'''

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import ds_pct

class PriceReverse1M(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 30
    author = 'fc'
    freq = 'daily'
    logic = '1个月股价反转'
    article = '广发证券-20170330-多因子Alpha系列报告之三十'
    basic_datas = {'daily': ['close_badj']}

    def st_factor(self):
        N = 20
        ret = ds_pct(self.database['daily']['close_badj'], N)

        return ret


    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    cal_factor()