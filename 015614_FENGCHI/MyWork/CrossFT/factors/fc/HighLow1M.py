# coding: utf-8
# Author：fengchi863
# Date ：2021/8/27 14:25

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import ds_max, ds_min


class HighLow1M(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 40
    author = 'fc'
    freq = 'daily'
    logic = '近一个月最低价和最高价之比'
    article = '爱建证券 20161128 – 多因子系列之二'
    basic_datas = {'daily': ['close_badj'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        close_badj = self.database['daily']['close_badj']
        high = ds_max(close_badj, 30)
        low = ds_min(close_badj, 30)
        return low / high

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    f = HighLow1M()
    f.save_result()
