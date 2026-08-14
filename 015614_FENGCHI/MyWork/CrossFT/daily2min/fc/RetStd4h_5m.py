# coding: utf-8
# Author：fengchi863
# Date ：2021/8/27 14:25

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *


class RetStd4h_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 1
    author = 'fc'
    freq = '5mins'
    logic = '近四小时的收益率的波动率在各行业的均值'
    article = '爱建证券 20161128 – 多因子系列之二'
    basic_datas = {'5mins': ['close_badj']}

    def st_factor(self):
        close = self.database['5mins']['close_badj']
        pct_chg = dt_pct(close, 1)
        ret_std = dt_std(pct_chg, 48)
        return ret_std

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    cal_factor()
