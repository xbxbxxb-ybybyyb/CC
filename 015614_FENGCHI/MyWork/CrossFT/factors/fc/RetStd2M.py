# coding: utf-8
# Author：fengchi863
# Date ：2021/8/27 14:25

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import ds_std


class RetStd2M(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 40
    author = 'fc'
    freq = 'daily'
    logic = '近两个月收益率的波动率在各行业的均值'
    article = '爱建证券 20161128 – 多因子系列之二'
    basic_datas = {'daily': ['pct_chg'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        pctchg = self.database['daily']['pct_chg']
        ret_std = ds_std(pctchg, 40)
        return ret_std

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    f = RetStd2M()
    f.save_result()
